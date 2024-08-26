import psycopg2
from django.conf import settings
from django.db import DatabaseError, IntegrityError, OperationalError, connections
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

from dataset.cabecalho_processual import CabecalhoProcessual
from dataset.infojud import DeclaracaoRenda, DeclaracaoRendaLista
from dataset.sisbajud import SisbajudContas, SisbajudOrdens


class NotConfiguredService(Exception):
    pass


class DatabaseBackend(BaseHealthCheckBackend):
    @classmethod
    def name(cls):
        return "db"

    def check_status(self):
        try:
            connection = connections["default"]
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
        except (IntegrityError, DatabaseError, OperationalError, psycopg2.Error):
            connection.close()
            raise ServiceUnavailable("Database error")

        cursor.close()


class GraphDatabaseBackend(BaseHealthCheckBackend):
    @classmethod
    def name(cls):
        return "graphdb"

    def check_status(self):
        create_query = "CREATE (n:Health {title: 'healthcheck'})"
        delete_query = "MATCH (n:Health {title: 'healthcheck'}) DELETE n"
        try:
            connection = connections[settings.GRAPH_DATABASE]
            cursor = connection.cursor()
            cursor.execute(create_query)
            cursor.execute(delete_query)
        except (IntegrityError, DatabaseError, OperationalError, psycopg2.Error):
            connection.close()
            raise ServiceUnavailable("Database error")

        cursor.close()


class CabecalhoProcessualBackend(BaseHealthCheckBackend):
    @classmethod
    def name(cls):
        return "cabecalho-processual"

    def check_status(self):
        if not settings.CABECALHO_PROCESSUAL_ENABLE:
            raise ServiceUnavailable("Service Cabeçalho Processual is disabled")
        if (
            not hasattr(settings, "CABECALHO_PROCESSUAL_HEALTH_USER")
            or not hasattr(settings, "CABECALHO_PROCESSUAL_HEALTH_DOCUMENT")
            or settings.CABECALHO_PROCESSUAL_HEALTH_USER == ""
            or settings.CABECALHO_PROCESSUAL_HEALTH_DOCUMENT == ""
        ):
            raise NotConfiguredService("Service 'Cabecalho Processual' not configured")
        try:
            api = CabecalhoProcessual(
                settings.CABECALHO_PROCESSUAL_API_URL,
                settings.CABECALHO_PROCESSUAL_TOKEN_URL,
                settings.CABECALHO_PROCESSUAL_CLIENT_ID,
                settings.CABECALHO_PROCESSUAL_CLIENT_SECRET,
            )
            processos = list(
                api.processos(
                    settings.CABECALHO_PROCESSUAL_HEALTH_USER,
                    settings.CABECALHO_PROCESSUAL_HEALTH_DOCUMENT,
                    itens=1,
                )
            )
            assert len(processos) > 0
        except Exception:
            raise ServiceUnavailable("Service 'Cabecalho Processual' error")


class SisbajudContasBackend(BaseHealthCheckBackend):
    @classmethod
    def name(cls):
        return "sisbajud-contas"

    def check_status(self):
        if not settings.SISBAJUD_CONTAS_ENABLE:
            raise ServiceUnavailable("Service Sisbajud is disabled")
        if (
            not hasattr(settings, "SISBAJUD_CONTAS_HEALTH_CPF_SOLICITANTE")
            or not hasattr(settings, "SISBAJUD_CONTAS_HEALTH_DOCUMENT_ENTIDADE")
            or not hasattr(settings, "SISBAJUD_CONTAS_HEALTH_TOKEN")
            or settings.SISBAJUD_CONTAS_HEALTH_CPF_SOLICITANTE == ""
            or settings.SISBAJUD_CONTAS_HEALTH_DOCUMENT_ENTIDADE == ""
            or settings.SISBAJUD_CONTAS_HEALTH_TOKEN == ""
        ):
            raise NotConfiguredService("Service 'Sisbajud Contas' not configured")
        try:
            api = SisbajudContas(settings.SISBAJUD_API_URL)
            api.execute(
                settings.SISBAJUD_CONTAS_HEALTH_CPF_SOLICITANTE,
                settings.SISBAJUD_CONTAS_HEALTH_DOCUMENT_ENTIDADE,
                settings.SISBAJUD_CONTAS_HEALTH_TOKEN,
            )
        except Exception:
            raise ServiceUnavailable("Service 'Sisbajud Contas' error")


class SisbajudOrdensBackend(BaseHealthCheckBackend):
    @classmethod
    def name(cls):
        return "sisbajud-ordens"

    def check_status(self):
        if not settings.SISBAJUD_ORDENS_ENABLE:
            raise ServiceUnavailable("Service Sisbajud is disabled")
        if (
            not hasattr(settings, "SISBAJUD_ORDENS_HEALTH_CPF")
            or not hasattr(settings, "SISBAJUD_ORDENS_HEALTH_TRIBUNAL")
            or settings.SISBAJUD_ORDENS_HEALTH_CPF == ""
            or settings.SISBAJUD_ORDENS_HEALTH_TRIBUNAL == ""
        ):
            raise NotConfiguredService("Service 'Sisbajud Ordens' not configured")
        try:
            api = SisbajudOrdens(settings.SISBAJUD_API_URL)
            api.execute(
                cpf_juiz=settings.SISBAJUD_ORDENS_HEALTH_CPF, cod_tribunal=settings.SISBAJUD_ORDENS_HEALTH_TRIBUNAL
            )
        except Exception:
            raise ServiceUnavailable("Service 'Sisbajud Ordens' error")


class DeclaracaoRendaListaBackend(BaseHealthCheckBackend):
    @classmethod
    def name(cls):
        return "infojud-lista"

    def check_status(self):
        if not settings.INFOJUD_ENABLE:
            raise ServiceUnavailable("Service Infojud is disabled")
        token_to_test = "dummy"
        try:
            DeclaracaoRendaLista(settings.INFOJUD_API_URL).execute(token_to_test)
        except Exception:
            raise ServiceUnavailable("Service 'Declaração Renda lista' error")


class DeclaracaoRendaDetalheBackend(BaseHealthCheckBackend):
    @classmethod
    def name(cls):
        return "infojud-detalhe"

    def check_status(self):
        if not settings.INFOJUD_ENABLE:
            raise ServiceUnavailable("Service Infojud is disabled")
        token_to_test = "dummy"
        cpf_cnpj_entidade = "12345678901"
        ano = 2023
        try:
            DeclaracaoRenda(settings.INFOJUD_API_URL).execute(token_to_test, cpf_cnpj_entidade, ano)
        except Exception:
            raise ServiceUnavailable("Service 'Declaração Renda detalhe' error")
