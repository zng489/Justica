import json
from functools import lru_cache
from unicodedata import normalize

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView
from urlid_graph.models import ElementConfig, ObjectRepository, get_nodes_and_properties
from urlid_graph.serializers import DetailedEdgeSerializer
from urlid_graph.views import AllNodesRelationshipsEndpoint, GraphNodeDetailEndpoint, NodeRelationshipsEndpoint
from urlid_graph.views import SearchOnGraphEndpoint as OriginalSearchOnGraphEndpoint

from authentication.models import SocialLogin
from authentication.utils import is_magistrado
from core.serializers import ExtraNodeSerializer
from dataset.models import Company, Person
from dataset.utils import cnpj_checks
from health.core import run_checks


class MainView(TemplateView):
    template_name = "core/main.html"


class PingView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "pong!"})


def zabbix_view(request):
    report = run_checks()
    return JsonResponse(report)


@lru_cache(maxsize=1)
def get_config():
    with open(settings.BASE_DIR / "config" / "config.json") as fobj:
        return json.load(fobj)


def get_user_data(request, data):
    from dataset.formatting import format_cpf

    user = request.user
    name = data.get("name") or data.get("given_name") or user.first_name
    cpf = data.get("preferred_username") or user.username
    # TODO: cache ElementConfig as in `processos` view
    terms_config = ElementConfig.objects.filter(config_type=ElementConfig.CUSTOM_CONFIG, name="terms").first()
    title = terms_config.data.get("title") if terms_config is not None else ""
    template = terms_config.data.get("template") if terms_config is not None else ""
    return {
        "name": name,
        "cpf": format_cpf(cpf) if cpf else "",
        "terms": {
            "accepted_at": data.get("accepted_terms_at"),
            "title": title,
            "template": template,
        },
        "juiz": is_magistrado(request.decoded_token, settings.MAGISTRADO_PROFILES),
    }


def config(request):
    config = get_config()
    config["integrations"] = {
        "CABECALHO_PROCESSUAL": settings.CABECALHO_PROCESSUAL_ENABLE,
        "SISBAJUD_CONTAS": settings.SISBAJUD_CONTAS_ENABLE,
        "SISBAJUD_ORDENS": settings.SISBAJUD_ORDENS_ENABLE,
        "INFOJUD": settings.INFOJUD_ENABLE,
    }
    if not isinstance(request.user, AnonymousUser):
        social_login = SocialLogin.objects.filter(user=request.user).first()
        if social_login is not None:
            config["user"] = get_user_data(request, social_login.extra_data)
    return JsonResponse(config)


@require_http_methods(["POST"])
def accept_terms(request):
    social_login = SocialLogin.objects.filter(user=request.user).first()
    if social_login is not None:
        if social_login.extra_data.get("accepted_terms_at") is not None:
            return HttpResponseBadRequest()
        else:
            social_login.extra_data["accepted_terms_at"] = str(timezone.now())
            social_login.save()
    else:
        return HttpResponseNotFound()

    return JsonResponse(dict())


class ExtraAllNodesRelationshipsEndpoint(AllNodesRelationshipsEndpoint):
    serializer_class = ExtraNodeSerializer
    node_serializer_class = ExtraNodeSerializer


class ExtraGraphNodeDetailEndpoint(GraphNodeDetailEndpoint):
    serializer_class = ExtraNodeSerializer
    node_serializer_class = ExtraNodeSerializer
    edge_serializer_class = DetailedEdgeSerializer

    def get(self, request, uuid):
        uuid = str(uuid)
        nodes = {str(obj.uuid): obj for obj in get_nodes_and_properties(uuids=[uuid], serialize_method="both")}
        obj = nodes.get(uuid)
        if not obj:
            raise Http404

        data = self.get_serializer_class()(obj).data
        nodes, edges = self.graph.get_relationships(**self.get_relationships_kwargs(uuids=uuid))
        data["graph"] = self.serialize_graph(nodes, edges)
        return Response(data)


class ExtraNodeRelationshipsEndpoint(NodeRelationshipsEndpoint):
    serializer_class = ExtraNodeSerializer
    node_serializer_class = ExtraNodeSerializer
    edge_serializer_class = DetailedEdgeSerializer


def version(request):
    filename = settings.BASE_DIR / "config" / "version.txt"
    if not filename.exists():
        result = "Version file not found"
    else:
        with filename.open(mode="r") as fobj:
            result = fobj.read().strip()
    return HttpResponse(result)


class SearchOnGraphEndpoint(OriginalSearchOnGraphEndpoint):
    search_entities = ["person", "company", "candidacy"]
    search_max_items_per_entity = 10

    def get_search_term(self):
        term = self.request.GET.get("term", "").strip()
        # Remove ./- (documents)
        numbers = term.replace(".", "").replace("/", "").replace("-", "")
        if len(numbers) in (11, 14) and numbers.isdigit():
            if len(numbers) == 14 and numbers[8:12] != "0001":  # Filial
                # O usuário buscou pelo CNPJ de uma filial, mas o termo de busca é sobrescrito para conter o CNPJ da
                # matriz, assim o sistema encontrará a empresa (o banco de dados do Sniper tem apenas os CNPJs das
                # matrizes).
                numbers = numbers[:8] + "0001" + cnpj_checks(numbers[:8] + "0001")
            return numbers
        return normalize("NFKD", term).encode("ascii", errors="ignore").decode("ascii")  # Remove accents

    def get(self, *args, **kwargs):
        term = self.get_search_term()
        if not term:
            return Response([])

        # If the query is a CPF or CNPJ, return Person/Company directly
        if term.isdigit() and len(term) in (11, 14):
            Model, field = {11: (Person, "cpf"), 14: (Company, "cnpj")}[len(term)]
            obj = Model.objects.filter(**{field: term}).first()
            if obj is not None:
                results = ObjectRepository.objects.filter(uuid=obj.object_uuid)
                serialized_objects = self.serialize_search_result(results)
                return Response(serialized_objects)

        return super().get(*args, **kwargs)
