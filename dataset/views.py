from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from loguru import logger
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from urlid_graph.models import ElementConfig, ObjectRepository

from authentication.utils import get_codigo_tribunal
from core.logs.audit_logs_open_search import AuditLogsOpenSearch
from core.logs.utils import get_client_ip, get_localdate_dt, convert_ip_to_location

from . import formatting
from .cabecalho_processual import CabecalhoProcessual
from .decorators import enable_disable_endpoint
from .infojud import DeclaracaoRenda, DeclaracaoRendaLista, DeclaracaoRendaPJ
from .models import Company, Person
from .sisbajud import SisbajudContas, SisbajudOrdens


def get_keycloak_token(request):
    return getattr(request, "keycloak_token", None)


def get_decoded_token(request):
    return getattr(request, "decoded_token", None)


def get_custom_config(name, default=None):
    """Get custom config from ElementConfig model (24h cache)"""
    cache_key = f"dataset-config-{name}"
    result = cache.get(cache_key)
    if result is None:
        config = ElementConfig.objects.filter(
            config_type=ElementConfig.CUSTOM_CONFIG,
            name=name,
        ).first()
        result = config.data["content"] if config else default
        cache.set(cache_key, result, timeout=24 * 3600)
    return result


class ItemsJsonResponse:
    """Create JSON responses based on expected format to list items"""

    def __init__(self, title, fields, description=None):
        self._title = title
        self._fields = fields
        self._description = description
        self._status = 200
        self._error = False
        self._error_message = None
        self._items = []
        self._extra = {}

    def add(self, key, value):
        """Add new key/value to response"""
        self._extra[key] = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        if value:
            self._error = True
            self._error_message = value
        else:
            self._error = False
            self._error_message = None

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, value):
        self._items = value

    @property
    def data(self):
        if self._error:
            return {
                "error": self._error,
                "message": self._error_message,
            }
        return {
            "title": self._title,
            "description": self._description,
            "fields": self._fields,
            "results": self._items,
            **self._extra,
        }

    @property
    def response(self):
        return JsonResponse(self.data, status=self.status)


# TODO: add test
def get_document(repository: ObjectRepository, object_uuid):
    document = None
    obj = repository.objects.from_uuids([object_uuid]).first()
    if obj is None:
        return None

    if obj.entity.name == "person":
        person = Person.objects.filter(object_uuid=object_uuid).first()
        if person is None:
            return None
        document = str(person.cpf)
    elif obj.entity.name == "company":
        company = Company.objects.filter(object_uuid=object_uuid).first()
        if company is None:
            return None
        document = str(company.cnpj)
    else:
        raise ValueError("Object não encontrado")

    return document


@enable_disable_endpoint(settings.CABECALHO_PROCESSUAL_ENABLE)
def processos(request, object_uuid):
    # TODO: add pagination
    title = get_custom_config("cabecalho-processual-title", default="Lista de processos")
    description = get_custom_config(
        name="cabecalho-processual-description",
        default="Por conta de limitações no sistema de Cabeçalho Processual, apenas os últimos processos estão sendo exibidos.",
    )
    response_builder = ItemsJsonResponse(
        title=title,
        description=description,
        fields=CabecalhoProcessual.fields,
    )

    if not settings.CABECALHO_PROCESSUAL_CLIENT_ID or not settings.CABECALHO_PROCESSUAL_CLIENT_SECRET:
        response_builder.error = "Integração não configurada"
        return response_builder.response

    opensearch = AuditLogsOpenSearch(
        settings.OPENSEARCH_URL, settings.OPENSEARCH_PORT, settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD
    )

    api = CabecalhoProcessual(
        settings.CABECALHO_PROCESSUAL_API_URL,
        settings.CABECALHO_PROCESSUAL_TOKEN_URL,
        settings.CABECALHO_PROCESSUAL_CLIENT_ID,
        settings.CABECALHO_PROCESSUAL_CLIENT_SECRET,
    )
    has_error, document = False, None
    try:
        document = get_document(ObjectRepository, object_uuid)
    except ValueError:
        has_error = True
    if has_error or document is None:
        response_builder.error = "Objeto não encontrado"
        return response_builder.response

    try:
        result = api.processos(request.user.username, document, itens=10)
    except OAuth2Error:
        import traceback

        logger.error(traceback.format_exc())
        response_builder.error = "Erro ao autenticar"
        response_builder.status = 403
        return response_builder.response

    if not result:
        response_builder.description = "Nenhum processo encontrado"
        return response_builder.response

    client_ip, port = request.get_host(), request.get_port()

    logger.info(f"ClientIP {client_ip}:{port}")

    df = convert_ip_to_location(
        ip_address=[client_ip],
        params=['lat', 'lon', 'country', 'countryCode', 'city', 'timezone'])

    data = {
        "argumentosPesquisa": object_uuid,
        "cnpjPesquisado": document,
        "cpfUsuarioConsulta": request.user.username,
        "detalhesParametrosPesquisa": {"servico": "busca-cabecalho-processual", "pais": df.get('country'), "cidade": df.get('city')},
        "nomeUsuarioConsulta": request.user.username,
        "pesquisaTimestamp": get_localdate_dt(),
        "quantidadeResultados": len(result),
        "remoteAddr": get_client_ip(request),
        "remotePort": port,
        "usuarioGeoIP": {"lat": df.get('lat'), "lon": df.get('lon')},
    }
    # Grava logs de auditoria
    opensearch.grava_log_from_params("datajud", data)
    new_result = []
    for processo in result:
        for parte in processo["partes"]:
            if len(parte["documento"]) == 11:
                parte["documento"] = formatting.format_cpf(parte["documento"])
            elif len(parte["documento"]) == 14:
                parte["documento"] = formatting.format_cnpj(parte["documento"])
            del parte["tipo"]
        new_result.append(processo)
    response_builder.items = new_result
    return response_builder.response


@enable_disable_endpoint(settings.SISBAJUD_CONTAS_ENABLE)
def sisbajud_contas(request, object_uuid):
    title = get_custom_config("sisbajud-contas-title", default="Contas em instituições financeiras")
    description = get_custom_config("sisbajud-contas-description", default="")
    response_builder = ItemsJsonResponse(
        title=title,
        description=description,
        fields=SisbajudContas.fields,
    )

    has_error, document = False, None
    try:
        document = get_document(ObjectRepository, object_uuid)
    except ValueError:
        has_error = True
    if has_error or document is None:
        response_builder.error = "Objeto não encontrado"
        return response_builder.response

    api = SisbajudContas(settings.SISBAJUD_API_URL)
    try:
        result = api.execute(request.user.username, document, token=get_keycloak_token(request))
    except Exception:
        import traceback

        logger.error(traceback.format_exc())
        response_builder.error = "Erro ao obter dados"
        return response_builder.response

    response_builder.items = result

    # obtêm o IP do cliente
    client_ip, port = request.get_host(), request.get_port()

    logger.info(f"ClientIP {client_ip}:{port}")

    data = {
        "argumentosPesquisa": object_uuid,
        "cnpjPesquisado": document,
        "cpfUsuarioConsulta": request.user.username,
        "nomeUsuarioConsulta": request.user.username,
        "pesquisaTimestamp": get_localdate_dt(),
        "quantidadeResultados": len(result),
        "remoteAddr": get_client_ip(request),
        "remotePort": port,
    }
    opensearch = AuditLogsOpenSearch(
        settings.OPENSEARCH_URL, settings.OPENSEARCH_PORT, settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD
    )

    opensearch.grava_log_from_params("sisbajud-contas", data)

    return response_builder.response


@enable_disable_endpoint(settings.SISBAJUD_ORDENS_ENABLE)
def sisbajud_ordens(request):
    title = get_custom_config("sisbajud-ordens-title", default="Lista de ordens de quebra de sigilo")
    description = get_custom_config("sisbajud-ordens-description", default="")
    response_builder = ItemsJsonResponse(
        title=title,
        description=description,
        fields=SisbajudOrdens.fields,
    )

    cpf_juiz = request.GET.get("cpf") or request.user.username
    api = SisbajudOrdens(settings.SISBAJUD_API_URL)
    try:
        silent = "fakeapi" in settings.SISBAJUD_API_URL
        cod_tribunal = get_codigo_tribunal(get_decoded_token(request), silent=silent)
        result = api.execute(cpf_juiz=cpf_juiz, cod_tribunal=cod_tribunal)
    except Exception:
        import traceback

        logger.error(traceback.format_exc())
        response_builder.error = "Erro ao obter dados"
        return response_builder.response

    nome_juiz = formatting.format_cpf(cpf_juiz)
    if person := Person.objects.filter(cpf=cpf_juiz).first():
        nome_juiz = f"{person.nome} ({nome_juiz})"
    response_builder.add("nome_juiz", nome_juiz)
    response_builder.items = result

    client_ip, port = request.get_host(), request.get_port()

    logger.info(f"ClientIP {client_ip}:{port}")

    data = {
        "argumentosPesquisa": cod_tribunal,
        "cnpjPesquisado": nome_juiz,
        "cpfUsuarioConsulta": cpf_juiz,
        "nomeUsuarioConsulta": nome_juiz,
        "pesquisaTimestamp": get_localdate_dt(),
        "quantidadeResultados": len(result),
        "remoteAddr": get_client_ip(request),
        "remotePort": port,
    }
    opensearch = AuditLogsOpenSearch(
        settings.OPENSEARCH_URL, settings.OPENSEARCH_PORT, settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD
    )

    opensearch.grava_log_from_params("sibsajud-ordens", data)

    return response_builder.response


@enable_disable_endpoint(settings.INFOJUD_ENABLE)
def declaracao_renda_lista(request):
    title = get_custom_config("infojud-lista-title", default="Infojud")
    description = get_custom_config("injojud-lista-description", default="")
    response_builder = ItemsJsonResponse(
        title=title,
        description=description,
        fields=DeclaracaoRendaLista.fields,
    )
    api = DeclaracaoRendaLista(settings.INFOJUD_API_URL)
    try:
        result = api.execute(get_keycloak_token(request))
    except Exception:
        import traceback

        logger.error(traceback.format_exc())
        response_builder.error = "Erro ao obter dados"
        return response_builder.response

    response_builder.items = result
    client_ip, port = request.get_host(), request.get_port()

    logger.info(f"ClientIP {client_ip}:{port}")

    ident_usuario_pesquisador = request.GET.get("cpf") or request.user.username

    data = {
        "argumentosPesquisa": ident_usuario_pesquisador,
        "cnpjPesquisado": ident_usuario_pesquisador,
        "cpfUsuarioConsulta": ident_usuario_pesquisador,
        "nomeUsuarioConsulta": ident_usuario_pesquisador,
        "pesquisaTimestamp": get_localdate_dt(),
        "quantidadeResultados": len(result),
        "remoteAddr": get_client_ip(request),
        "remotePort": port,
    }
    opensearch = AuditLogsOpenSearch(
        settings.OPENSEARCH_URL, settings.OPENSEARCH_PORT, settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD
    )

    opensearch.grava_log_from_params("infojud-lista", data)

    return response_builder.response


@enable_disable_endpoint(settings.INFOJUD_ENABLE)
def declaracao_renda_detalhe(request, documento, ano):
    title = get_custom_config("infojud-detalhe-title", default="Infojud")
    description = get_custom_config("injojud-detalhe-description", default="")
    if len(documento) == 14:
        title = get_custom_config("infojud-detalhe-title", default="Infojud PJ")
        response_builder = ItemsJsonResponse(
            title=title,
            description=description,
            fields=DeclaracaoRendaPJ.fields,
        )
        api = DeclaracaoRendaPJ(settings.INFOJUD_API_URL)
    else:
        title = get_custom_config("infojud-detalhe-title", default="Infojud PF")
        response_builder = ItemsJsonResponse(
            title=title,
            description=description,
            fields=DeclaracaoRenda.fields,
        )
        api = DeclaracaoRenda(settings.INFOJUD_API_URL)
    try:
        result = api.execute(
            token=get_keycloak_token(request),
            cpf_cnpj_entidade=documento,
            ano=ano,
        )
    except Exception:
        import traceback

        logger.error(traceback.format_exc())
        response_builder.error = "Erro ao obter dados"
        return response_builder.response

    response_builder.items = result

    client_ip, port = request.get_host(), request.get_port()

    logger.info(f"ClientIP {client_ip}:{port}")

    ident_usuario_pesquisador = request.GET.get("cpf") or request.user.username

    data = {
        "argumentosPesquisa": documento,
        "cnpjPesquisado": documento,
        "cpfUsuarioConsulta": ident_usuario_pesquisador,
        "nomeUsuarioConsulta": ident_usuario_pesquisador,
        "pesquisaTimestamp": get_localdate_dt(),
        "quantidadeResultados": len(result),
        "remoteAddr": get_client_ip(request),
        "remotePort": port,
    }
    opensearch = AuditLogsOpenSearch(
        settings.OPENSEARCH_URL, settings.OPENSEARCH_PORT, settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD
    )

    opensearch.grava_log_from_params("infojud", data)
    return response_builder.response


@enable_disable_endpoint(settings.AUDITORIA_ENABLE)
def auditoria_logs(request):
    '''
    Log every audit request, storing at the OpenSearch
    '''

    cpf_juiz = request.GET.get("cpf") or request.user.username

    nome_juiz = formatting.format_cpf(cpf_juiz)
    if person := Person.objects.filter(cpf=cpf_juiz).first():
        nome_juiz = f"{person.nome} ({nome_juiz})"

    client_ip, port = request.get_host(), request.get_port()

    logger.info(f"ClientIP {client_ip}:{port}")

    data = {
        "argumentosPesquisa": nome_juiz,
        "cnpjPesquisado": nome_juiz,
        "cpfUsuarioConsulta": cpf_juiz,
        "nomeUsuarioConsulta": nome_juiz,
        "pesquisaTimestamp": get_localdate_dt(),
        "quantidadeResultados": 1,
        "remoteAddr": get_client_ip(request),
        "remotePort": port,
    }
    opensearch = AuditLogsOpenSearch(
        settings.OPENSEARCH_URL, settings.OPENSEARCH_PORT, settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD
    )

    opensearch.grava_log_from_params("sibsajud-ordens", data)

    return