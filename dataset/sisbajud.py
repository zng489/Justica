import datetime
from urllib.parse import urljoin

import requests
from django.conf import settings
from loguru import logger

from dataset.formatting import format_cpf_cnpj, format_datetime
from dataset.utils import cnpj_checks, uuid_from_document


class Sisbajud:
    def __init__(self, api_url):
        self.api_url = api_url
        self.session = requests.Session()


class SisbajudContas(Sisbajud):
    fields = [
        {
            "name": "nome",
            "title": "Nome",
            "type": "string",
            "description": "Nome da instituição financeira",
        },
        {
            "name": "cnpj",
            "title": "CNPJ",
            "type": "string",
            "description": "CNPJ da instituição financeira",
        },
        {
            "name": "ativa",
            "title": "Ativa",
            "type": "bool",
            "description": "Conta ativa ou não",
        },
    ]

    def get(self, cpf_solicitante, cpf_cnpj_entidade, token):
        url = urljoin(self.api_url, f"v1/relacionamento/{cpf_cnpj_entidade}")
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.get(url, headers=headers, params={"cpfUsuarioSolicitante": cpf_solicitante})
        if response.ok:
            return response.json().get("contas", []) or []
        else:
            logger.error(f"Error accessing endpoint {self.api_url}: {response.status_code} - {response.content}")
            return []

    def parse_results(self, raw_result):
        result = []
        for row in raw_result:
            nome = row.get("nomeInstituicaoFinanceira")
            codigo = row.get("codigoInstituicaoFinanceira")
            cnpj = row.get("cnpjInstituicaoFinanceira")
            if codigo:
                nome += f" ({codigo})"
            if cnpj and len(cnpj) == 8:
                cnpj = cnpj + "0001" + cnpj_checks(cnpj + "0001")

            result.append(
                [
                    nome,
                    format_cpf_cnpj(cnpj) or None,
                    row.get("ativo"),
                ]
            )
        return result

    def execute(self, cpf_solicitante, cpf_cnpj_entidade, token):
        return self.parse_results(self.get(cpf_solicitante, cpf_cnpj_entidade, token))


class SisbajudOrdens(Sisbajud):
    fields = [
        [
            {
                "name": "numero_processo",
                "title": "Processo",
                "type": "string",
                "description": "Número do Processo",
            },
            {
                "name": "protocolo",
                "title": "Protocolo",
                "type": "string",
                "description": "Número do Protocolo",
            },
            {
                "name": "data_protocolamento",
                "title": "Data Protoc.",
                "type": "string",
                "description": "Data do Protocolamento",
            },
            {
                "name": "tipo_ordem",
                "title": "Tipo",
                "type": "string",
                "description": "Tipo da Ordem",
            },
            {
                "name": "descricao_situacao",
                "title": "Situação",
                "type": "string",
                "description": "Situação",
            },
            {
                "name": "tribunal",
                "title": "Tribunal",
                "type": "string",
                "description": "Tribunal",
            },
            {
                "name": "vara",
                "title": "Vara",
                "type": "string",
                "description": "Vara",
                "show": False,
            },
            {
                "name": "nome_juiz",
                "title": "Juiz",
                "type": "string",
                "description": "Nome do Juiz",
            },
            {
                "name": "nome_assessor",
                "title": "Assessor",
                "type": "string",
                "description": "Nome do Assessor",
                "show": False,
            },
            {
                "name": "partes",
                "title": "Réus",
                "type": "string",
                "description": "Lista de réus",
            },
        ],
        [
            {
                "name": "nome",
                "title": "Nome",
                "type": "string",
                "description": "Nome réu",
            },
            {
                "name": "documento",
                "title": "Documento",
                "type": "string",
                "description": "Documento",
            },
            {
                "name": "valor",
                "title": "Valor a bloquear",
                "type": "numeric",
                "description": "Soma de valores a bloquear",
            },
            {
                "name": "conta_salario",
                "title": "Conta Salário",
                "type": "bool",
                "description": "Conta Salário",
                "show": False,
            },
            {
                "name": "object_uuid",
                "title": "Object UUID",
                "type": "uuid",
                "description": "UUID",
                "show": False,
            },
        ],
    ]

    def __init__(
        self,
        api_url,
        auth_url=None,
        username=None,
        password=None,
        client_id=None,
        client_secret=None,
        grant_type="password",
    ):
        super().__init__(api_url)
        self.auth_url = auth_url or settings.OPENID_AUTH_URL
        self.username = username or settings.SISBAJUD_API_USERNAME
        self.password = password or settings.SISBAJUD_API_PASSWORD
        self.client_id = client_id or settings.SISBAJUD_API_CLIENT_ID
        self.client_secret = client_secret or settings.SISBAJUD_API_CLIENT_SECRET
        self.grant_type = grant_type

    def get_token(self):
        if "fakeapi" in self.api_url or "http://keycloak:" in self.auth_url:
            return None
        # TODO: maybe cache with lru_cache and check exp time
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
            "grant_type": self.grant_type,
        }
        resp = self.session.post(self.auth_url, data=payload)
        return resp.json()["access_token"]

    def get(self, cpf_juiz, cod_tribunal, token):
        params = {
            "bloqueioSemDesdobramento": "",
            "codAssessor": "",
            "codComarca": "",
            "codJuizDestinatario": cpf_juiz.replace("-", "").replace(".", ""),
            "codOrdemJudicial": "",
            "codProcesso": "",
            "codReuExecutado": "",
            "codTransferencia": "",
            "codTribunal": cod_tribunal,
            "codVara": "",
            "colunaAtiva": "",
            "dataFimProtocolo": "",
            "dataFimUltimoProtocolo": "",
            "dataInicioProtocolo": "",
            "dataInicioUltimoProtocolo": "",
            "direcaoPaginacao": "1",
            "incluirCancelados": "",
            "lida": "",
            "liquidacaoExtrajudicial": "",
            "ordenacaoAsc": "0",
            "pageIndex": "0",
            "pendente": "",
            "protocolo": "",
            "semRepeticao": "",
            "tipoOrdemInicial": "",
            "tipoSituacao": "",
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.get(
            urljoin(self.api_url, "v1/ordem"),
            headers=headers,
            params=params,
        )
        logger.error(f"Requesting SisbajudOrdens {response.request.url} / {response.url}")
        if response.ok:
            return response.json().get("content", []) or []
        else:
            logger.error(f"Error accessing endpoint {self.api_url}: {response.status_code} - {response.content}")
            return []

    def get_partes(self, lista_reus):
        data = []
        for row in lista_reus:
            documento = str(row.get("cpfCnpjExecutado"))
            new = {
                "nome": row.get("nomeExecutado"),
                "documento": format_cpf_cnpj(documento),
                "valor": row.get("valorAplicado"),
                "conta_salario": row.get("contaSalario"),
            }
            _, new["object_uuid"] = uuid_from_document(documento)
            data.append(new)

        return data

    def parse_results(self, raw_result):
        result = []
        for row in raw_result:
            numero_processo = row.get("codProcesso")
            lista_reus = row.get("listaReus", []) or []
            # link_processo = link_ordem_judicial = None
            # numero_ordem_judicial = row.get("codOrdemJudicial")
            # if settings.MARKETPLACE_URL and numero_processo:
            #     link_processo = urljoin(settings.MARKETPLACE_URL, f"pdpj/processo/{numero_processo}")
            # link_ordem_judicial = None
            # if numero_ordem_judicial:
            #     link_ordem_judicial = urljoin(self.api_url, f"ordem-judicial/{numero_ordem_judicial}/detalhar")
            datahora_protocolamento = row.get("dataHoraProtocolamento")
            if datahora_protocolamento is not None:
                try:
                    datahora_protocolamento = datetime.datetime.strptime(datahora_protocolamento, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
                else:
                    try:
                        datahora_protocolamento = format_datetime(datahora_protocolamento)
                    except AttributeError:
                        pass
            result.append(
                {
                    "numero_processo": numero_processo,
                    "protocolo": row.get("protocolo"),
                    "data_protocolamento": datahora_protocolamento,
                    "tipo_ordem": row.get("descricaoTipoOrdem"),
                    "nome_juiz": row.get("nomeJuiz"),
                    "tribunal": row.get("nomeTribunal"),
                    "partes": self.get_partes(lista_reus),
                    "descricao_situacao": row.get("descricaoSituacao"),
                    "nome_assessor": row.get("nomeAssessor"),
                    "vara": row.get("varaJuizo"),
                }
            )

        return result

    def execute(self, cpf_juiz, cod_tribunal):
        token = self.get_token()
        return self.parse_results(self.get(cpf_juiz, cod_tribunal, token))
