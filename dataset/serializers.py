import datetime

from urlid_graph.serializers import RelationshipSerializer

from dataset import choices
from dataset.formatting import format_cnpj, format_cpf, format_date
from dataset.utils import cnpj_checks

EMPRESA_QUALIFICACAO_SOCIO_DICT = dict(choices.EMPRESA_QUALIFICACAO_SOCIO)
PAIS_DICT = dict(choices.PAIS)
TIPO_SOCIO_DICT = {1: "Pessoa jurídica", 2: "Pessoa física"}


def parse_date(value):
    return datetime.datetime.strptime(value, "%Y-%m-%d").date()


class RelationshipMappingSerializer(RelationshipSerializer):
    """RelationshipSerializer which reads `self.mapping` to serialize field values"""

    @property
    def data(self):
        result = self.obj["properties"].copy()
        for key, configs in self.mapping.items():
            value = result.pop(key, None)
            if value:
                result[configs["label"]] = configs["value"](value)
        return result


class RunsForSerializer(RelationshipSerializer):
    name = "runs_for"

    @property
    def label(self):
        return "Candidatou-se"

    @property
    def data(self):
        return self.obj["properties"]


class RepresentsSerializer(RelationshipSerializer):
    name = "represents"

    @property
    def data(self):
        result = self.obj["properties"].copy()
        cnpj_raiz = result.pop("cnpj_raiz", [])
        codigo_qualificacao_representante = result.pop("codigo_qualificacao_representante", [])
        if cnpj_raiz and codigo_qualificacao_representante and len(cnpj_raiz) == len(codigo_qualificacao_representante):
            for index, (cnpj, codigo) in enumerate(zip(cnpj_raiz, codigo_qualificacao_representante), start=1):
                cnpj = format_cnpj(cnpj + "0001" + cnpj_checks(cnpj + "0001"))
                qualificacao = EMPRESA_QUALIFICACAO_SOCIO_DICT.get(int(codigo), codigo)
                if index == 1 and len(cnpj_raiz) == 1:
                    label = "Qualificação/CNPJ"
                else:
                    label = f"Qualificação/CNPJ (empresa {index})"
                result[label] = f"{qualificacao} ({cnpj})"
        return result

    @property
    def label(self):
        return "Representante legal"


class PartnerSerializer(RelationshipMappingSerializer):
    name = "is_partner"
    mapping = {
        "codigo_qualificacao": {
            "label": "Qualificação",
            "value": lambda codigo: EMPRESA_QUALIFICACAO_SOCIO_DICT.get(int(codigo), codigo),
        },
        "codigo_qualificacao_representante": {
            "label": "Qualificação do representante",
            "value": lambda codigo: EMPRESA_QUALIFICACAO_SOCIO_DICT.get(int(codigo), codigo),
        },
        "cpf_representante_legal": {
            "label": "CPF do representante legal",
            "value": lambda cpf: format_cpf(cpf),
        },
        "data_entrada_sociedade": {
            "label": "Data de entrada na sociedade",
            "value": lambda data: format_date(parse_date(data)),
        },
        "codigo_pais": {"label": "País", "value": lambda codigo: PAIS_DICT.get(int(codigo), codigo)},
        "codigo_tipo_socio": {
            "label": "Tipo de sócio",
            "value": lambda codigo: TIPO_SOCIO_DICT.get(int(codigo), codigo),
        },
    }

    @property
    def label(self):
        codigo_qualificacao = self.obj.get("properties", {}).get("codigo_qualificacao", None)
        if not codigo_qualificacao:
            return "Sócio(a)"
        return self.mapping["codigo_qualificacao"]["value"](codigo_qualificacao)
