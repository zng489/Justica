import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from opensearch_dsl import Document, Integer, Ip, Keyword, Search, Text
from opensearchpy import OpenSearch

from core.logs.utils import get_id_random_string, get_localdate_dt, convert_ip_to_location, convert_ip_to_location_geoip

index_name = "sniper_audit_logs"


class SniperAuditLogs(Document):
    auditID = Keyword()
    remoteAddr = Ip()
    remotePort = Integer()
    cnpjPesquisado = Keyword()
    argumentosPesquisa = Text()
    cpfUsuarioConsulta = Keyword()
    # pesquisaTimestamp = Date()

    class Index:
        name = index_name

    def save(self, **kwargs):
        return super(SniperAuditLogs, self).save(**kwargs)


class AuditLogsOpenSearch:

    def __init__(self, open_search_url, open_search_port, open_search_user, open_search_passwd):
        self.__open_search_user, self.__open_search_passwd = open_search_user, open_search_passwd
        self.open_search_url = open_search_url
        self.open_search_port = open_search_port
        self.session = requests.Session()
        # Create the client with SSL/TLS enabled, but hostname verification disabled.
        self.client = OpenSearch(
            hosts=[{"host": self.open_search_url, "port": self.open_search_port}],
            http_compress=False,  # enables gzip compression for request bodies
            http_auth=(self.__open_search_user, self.__open_search_passwd),
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

    def grava_log(self, data):
        # Index your data into OpenSearch
        response = self.client.index(index=index_name, body=data)

        return response

    def grava_log_from_params(self, servico, data_params: dict):
        # Index your data into OpenSearch
        df = convert_ip_to_location_geoip(
            ip_address=[data_params["remoteAddr"]],
            params=['lat', 'lon', 'country', 'countryCode', 'city', 'timezone'])

        data = {
                "@timestamp": get_localdate_dt(),
                "argumentosPesquisa": data_params["argumentosPesquisa"],
                "auditID": get_id_random_string(15),
                "cnpjPesquisado": data_params["cnpjPesquisado"],
                "cpfUsuarioConsulta": data_params["cpfUsuarioConsulta"],
                "detalhesParametrosPesquisa": {"servico": servico, "pais": df.get('country_name'),
                                               "cidade": df.get('city'), "paisCodigo": df.get('country_code'),
                                               "continente": df.get('continent_name')},
                "nomeUsuarioConsulta": data_params["nomeUsuarioConsulta"],
                "pesquisaTimestamp": data_params["pesquisaTimestamp"],
                "quantidadeResultados": data_params["quantidadeResultados"],
                "remoteAddr": data_params["remoteAddr"],
                "remotePort": data_params["remotePort"],
                # "resultadoPesquisa": {"result1": "value1", "result2": "value2"},
                # "usuarioExtraData": {"extra1": "value1", "extra2": "value2"},
                "usuarioGeoIP": {"lat": df.get("latitude"), "lon": df.get("longitude")},
        }

        # Index your data into OpenSearch
        response = self.client.index(index=index_name, body=data)

        return response

    def pesquisa_log(self, id):
        s = Search(using=open_search.client, index=index_name).query("match", auditID=id)

        s.execute()

    @property
    def access_token(self):
        if "fakeapi" in self.base_url:
            return None
        if self.__token is None or self.__token["expires_at"] < time.time():
            self._get_token(self.__client_id, self.__client_secret)
        return self.__token["access_token"]

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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--open_search_url")
    parser.add_argument("--open_search_port")
    parser.add_argument("--open_search_user", help="Usuário de acesso ao OpenSearch")
    parser.add_argument("--open_search_password", help="Senha de acesso ao OpenSearch")
    args = parser.parse_args()

    host = "opensearch.stg.pdpj.jus.br"
    port = 443
    f = open("passw.txt", "r")
    passw = f.read()
    print(passw)
    auth = ("rosfran.borges", passw)

    print(args.open_search_url, args.open_search_port, args.open_search_user, args.open_search_password)

    open_search = AuditLogsOpenSearch(
        args.open_search_url, args.open_search_port, args.open_search_user, args.open_search_password
    )

    data = {
        "@timestamp": "2024-03-21T12:00:00",
        "argumentosPesquisa": "example arguments",
        "auditID": "X91919ID",
        "cnpjPesquisado": "example_cnpj",
        "cpfUsuarioConsulta": "example_cpf",
        "detalhesParametrosPesquisa": {"param1": "value1", "param2": "value2"},
        "nomeUsuarioConsulta": "example_username",
        "pesquisaTimestamp": "2024-03-21T12:00:00",
        "quantidadeResultados": 10,
        "remoteAddr": "192.168.1.1",
        "remotePort": 12345,
        "resultadoPesquisa": {"result1": "value1", "result2": "value2"},
        "usuarioExtraData": {"extra1": "value1", "extra2": "value2"},
        "usuarioGeoIP": {"lat": 40.12, "lon": -71.34},
    }

    # Index your data into OpenSearch
    response = open_search.grava_log(data)

    print("Data stored successfully. " + str(response))

    result = [34, 22, 11]
    document = "00855430"
    params = {
        "argumentosPesquisa": document,
        "auditID": get_id_random_string(15),
        "cnpjPesquisado": document,
        "cpfUsuarioConsulta": "rr",
        # "detalhesParametrosPesquisa": {"param1": "value1", "param2": "value2"},
        "nomeUsuarioConsulta": "rr",
        "quantidadeResultados": len(result),
        "remoteAddr": "192.189.19.1",
        "remotePort": 2929,
        "pesquisaTimestamp": datetime.now(),
        # "resultadoPesquisa": {"result1": "value1", "result2": "value2"},
        # "usuarioExtraData": {"extra1": "value1", "extra2": "value2"},
        "usuarioGeoIP": {"lat": 40.12, "lon": -71.34},
    }
    open_search.grava_log_from_params(params)

    print(open_search.pesquisa_log("example_audit_log"))
