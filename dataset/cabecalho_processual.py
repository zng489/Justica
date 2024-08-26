import csv
import datetime
import time
from functools import lru_cache
from urllib.parse import urljoin

import requests
from django.core.cache import cache
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from dataset.formatting import format_datetime, format_numero_processo
from dataset.utils import uuid_from_document


def lista_classes_processuais():
    """Devolve lista de classes processuais simplificada a partir da API TPU

    Usa o cache do Django para armazenar o valor por 24 horas, para evitar
    chamadas desnecessárias.
    """
    cache_key = "dataset-cabecalho-processual-classes"
    result = cache.get(cache_key)
    if result is None:
        url = "https://gateway.cloud.pje.jus.br/tpu/api/v1/publico/download/classes"
        data = requests.get(url).json()
        result = {int(row["cod_item"]): {key: row.get(key) for key in ("cod_item_pai", "nome")} for row in data}
        cache.set(cache_key, result, timeout=24 * 3600)
    return result


@lru_cache(maxsize=1024)
def arvore_classe_processual(codigo):
    """Devolve a lista de nomes de uma determinada classe processual, até a raiz"""
    classes = lista_classes_processuais()
    error = False
    try:
        codigo = int(codigo) if codigo else None
    except (TypeError, ValueError):
        error = True
    if error or not codigo or codigo not in classes:
        return [str(codigo or "").strip()]

    classe = classes[codigo]
    result = [classe["nome"]]
    while classe["cod_item_pai"]:
        new = classes.get(classe["cod_item_pai"])
        if new is None:
            break
        classe = new
        result.append(classe["nome"])
    result.reverse()
    return result


def lista_movimentos_processuais():
    """Devolve lista de movimentos simplificada a partir da API TPU

    Usa o cache do Django para armazenar o valor por 24 horas, para evitar
    chamadas desnecessárias.
    """
    cache_key = "dataset-cabecalho-processual-movimentos"
    result = cache.get(cache_key)
    if result is None:
        url = "https://gateway.cloud.pje.jus.br/tpu/api/v1/publico/download/movimentos"
        data = requests.get(url).json()
        result = {row["id"]: {key: row.get(key) for key in ("cod_item_pai", "movimento")} for row in data}
        cache.set(cache_key, result, timeout=24 * 3600)
    return result


@lru_cache(maxsize=1024)
def nome_movimento_processual(codigo):
    """Devolve o nome de um determinado movimento processual"""
    movimentos = lista_movimentos_processuais()
    error = False
    try:
        codigo = int(codigo) if codigo else None
    except (TypeError, ValueError):
        error = True
    if error or not codigo or codigo not in movimentos:
        return str(codigo or "").strip()
    return movimentos[codigo]["movimento"]


class CabecalhoProcessual:
    fields = [
        [
            {
                "name": "numero",
                "title": "Número",
                "type": "string",
                "description": "Número do Processo",
            },
            {
                "name": "tribunal",
                "title": "Tribunal",
                "type": "string",
                "description": "Tribunal",
            },
            {
                "name": "classe",
                "title": "Classe",
                "type": "string",
                "description": "Árvore de classes do processo",
            },
            {
                "name": "assunto",
                "title": "Assunto",
                "type": "string",
                "description": "Assunto",
                "show": False,
            },
            {
                "name": "ultimo_movimento",
                "title": "Últ. movimento",
                "type": "string",
                "description": "Último movimento no processo",
            },
            {
                "name": "datahora_ultimo_movimento",
                "title": "Data/hora últ. movimento",
                "type": "string",
                "description": "Data/hora do último movimento no processo",
            },
            {
                "name": "partes",
                "title": "Partes",
                "type": "list",
                "description": "Partes do processo",
            },
        ],
        [
            {"name": "nome", "title": "Nome", "type": "string", "description": "Nome"},
            {"name": "documento", "title": "CPF/CNPJ", "type": "string", "description": "CPF ou CNPJ"},
            {
                "name": "object_uuid",
                "title": "UUID",
                "type": "uuid",
                "description": "UUID do objeto",
                "show": False,
            },
        ],
    ]

    def __init__(self, api_url, token_url, client_id, client_secret):
        self.__client_id, self.__client_secret = client_id, client_secret
        self.__token = None
        self.base_url = api_url
        self.token_url = token_url
        self.session = requests.Session()

    @property
    def access_token(self):
        if "fakeapi" in self.base_url:
            return None
        if self.__token is None or self.__token["expires_at"] < time.time():
            self._get_token(self.__client_id, self.__client_secret)
        return self.__token["access_token"]

    def _get_token(self, client_id, client_secret):
        client = BackendApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        self.__token = oauth.fetch_token(
            token_url=self.token_url,
            client_id=client_id,
            client_secret=client_secret,
        )

    def request(self, method, path, documento_operador, params=None, timeout=None):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-PDPJ-CPF-USUARIO-OPERADOR": documento_operador,
        }
        response = self.session.request(
            method, urljoin(self.base_url, path), params=params, headers=headers, timeout=timeout
        )
        return response.json()

    def _processos(self, documento_operador, documento, itens=30):
        # TODO: implement pagination?
        params = {
            "cpfCnpj": documento,
            "pagina": 1,
            "quantidade": itens,
        }
        try:
            result = self.request("GET", "api/v1/processos/simples", documento_operador, params=params, timeout=25)
        except requests.exceptions.Timeout:
            result = {"code": 999, "message": "Timeout"}
        # TODO: analyze result["messages"] and log an error (?)

        # TODO: add auditing and logging facilities
        try:
            result = self.request("GET", "api/v1/processos/simples", documento_operador, params=params, timeout=25)
        except requests.exceptions.Timeout:
            result = {"code": 999, "message": "Timeout"}

        return result

    def processos(self, documento_operador, documento, itens=30):
        result = self._processos(documento_operador, documento, itens=itens)
        if not result or not isinstance(result, dict) or result.get("code") in (404, 500) or "result" not in result:
            return []

        data = []
        parte_header = "nome tipo documento object_uuid".split()
        for processo in result["result"]:
            partes = processo.get("partes", [])
            partes_formatadas = []
            if partes is not None:
                for parte in partes:
                    pessoa = parte.get("pessoa")
                    if not pessoa:
                        continue
                    nome = pessoa.get("nome")
                    documento_parte = pessoa.get("documento")
                    if not nome or not documento_parte:
                        continue
                    if len(documento_parte) not in (11, 14):
                        continue
                    tipo, object_uuid = uuid_from_document(documento_parte)
                    parte_tuple = (nome, tipo, documento_parte, object_uuid)
                    if parte_tuple not in partes_formatadas:
                        partes_formatadas.append(parte_tuple)
            ultimo_movimento = processo.get("ultimoMovimento", {}) or {}
            nome_movimento = nome_movimento_processual(ultimo_movimento.get("codigo"))
            if datahora_ultimo_movimento := ultimo_movimento.get("dataHora"):
                datahora_ultimo_movimento = datetime.datetime.strptime(str(datahora_ultimo_movimento), "%Y%m%d%H%M%S")
            classes_processuais = arvore_classe_processual(processo.get("classeProcessual"))
            assuntos = []
            for assunto in processo.get("assuntos", []) or []:
                nome = str(assunto.get("nome") or "").strip()
                if nome:
                    assuntos.append(nome)
            numero_processo = processo["numeroProcesso"]
            if numero_processo.lower().strip() != "processo sigiloso":
                numero_processo = format_numero_processo(numero_processo)
            data.append(
                {
                    "numero": numero_processo,
                    "classe": {"tree": classes_processuais} if classes_processuais else None,
                    "tribunal": processo.get("siglaTribunal"),
                    "assunto": ",".join(assuntos),
                    "ultimo_movimento": nome_movimento,
                    "datahora_ultimo_movimento": format_datetime(datahora_ultimo_movimento),
                    "partes": [dict(zip(parte_header, values)) for values in partes_formatadas],
                }
            )
        return data

    def movimentos(self, documento_operador, numero):
        return self.request("GET", f"api/v1/processos/{numero}/movimentos", documento_operador)


if __name__ == "__main__":
    import argparse
    import os

    import rows
    from tqdm import tqdm

    client_id = os.environ["CABECALHO_PROCESSUAL_CLIENT_ID"]
    client_secret = os.environ["CABECALHO_PROCESSUAL_CLIENT_SECRET"]

    parser = argparse.ArgumentParser()
    parser.add_argument("documento_operador")
    parser.add_argument("api_url")
    parser.add_argument("token_url")
    parser.add_argument(
        "input_filename", help="Arquivo CSV que contenha coluna 'documento', com os valores a serem buscados"
    )
    parser.add_argument(
        "output_filename", help="Arquivo CSV onde o resultado (partes + informações de processo) serão gravados"
    )
    args = parser.parse_args()

    api = CabecalhoProcessual(args.api_url, args.token_url, client_id, client_secret)
    with open(args.input_filename) as fobj:
        reader = csv.DictReader(fobj)
        if "documento" not in reader.fieldnames:
            import sys

            print("ERRO: o arquivo de origem precisa conter a coluna 'documento'", file=sys.stderr)
            exit(1)
        writer = rows.utils.CsvLazyDictWriter(args.output_filename)
        for row in tqdm(reader):
            for processo in api.processos(args.documento_operador, row["documento"]):
                for parte in processo["partes"]:
                    if not parte["nome"] or not parte["documento"]:
                        continue
                    writer.writerow(
                        {
                            "documento_busca": row["documento"],
                            "numero_processo": processo["resumo"]["numero"],
                            **parte,
                        }
                    )
        writer.close()
