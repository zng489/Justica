import json
from unittest import mock
from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory, override_settings
from model_bakery import baker
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from urlid_graph.models import ElementConfig

from dataset.fakedata import random_cnpj, random_cpf
from dataset.formatting import format_cpf
from dataset.models import Person
from dataset.views import declaracao_renda_detalhe, processos, sisbajud_contas, sisbajud_ordens

User = get_user_model()
SISBAJUD_CONTAS_FIELDS = [
    {"name": "nome", "title": "Nome", "type": "string", "description": "Nome instituição financeira"},
    {"name": "cnpj", "title": "CNPJ", "type": "string", "description": "CNPJ da Nome instituição financeira"},
    {"name": "agencia", "title": "Agência", "type": "string", "description": "Número da agência"},
    {"name": "conta", "title": "Conta", "type": "string", "description": "Número da conta"},
    {"name": "ativo", "title": "Ativo", "type": "bool", "description": "Conta ativa ou não"},
]


@pytest.mark.skip
@pytest.mark.django_db
class TestProcessos:
    @mock.patch("dataset.views.CabecalhoProcessual")
    @mock.patch("dataset.views.get_document", return_value="12345")
    def test_oauth2error(self, m_get_doc, m_CabecalhoProcessual, settings):
        settings.DEBUG = True
        m_api = mock.Mock()
        m_CabecalhoProcessual.return_value = m_api
        m_api.processos.side_effect = OAuth2Error

        object_uuid = uuid4()
        request = RequestFactory().get("v1/processos")
        cpf = random_cpf()
        request.user = baker.make(User, username=cpf)

        resp = processos(request, object_uuid)

        assert resp.status_code == 403
        m_CabecalhoProcessual.assert_called_once_with(
            settings.CABECALHO_PROCESSUAL_API_URL,
            settings.CABECALHO_PROCESSUAL_TOKEN_URL,
            settings.CABECALHO_PROCESSUAL_CLIENT_ID,
            settings.CABECALHO_PROCESSUAL_CLIENT_SECRET,
        )
        m_api.processos.assert_called_once_with(cpf, "12345", itens=10)


@pytest.mark.django_db
class TestSisbajudContasView:
    @mock.patch("dataset.views.SisbajudContas")
    def test_correct_response(self, m_SisbajudContas):
        title = "Sibajud contas title"
        description = "SisbajudContas description"
        baker.make(
            ElementConfig,
            config_type=ElementConfig.CUSTOM_CONFIG,
            name="sisbajud-contas-title",
            data={"content": title},
        )
        baker.make(
            ElementConfig,
            config_type=ElementConfig.CUSTOM_CONFIG,
            name="sisbajud-contas-description",
            data={"content": description},
        )

        m_api = mock.Mock()
        m_api.execute.return_value = [
            ["Banco do Brasil", "12345", True],
            ["Caixa Econômica", "54321", False],
        ]
        m_SisbajudContas.fields = SISBAJUD_CONTAS_FIELDS
        m_SisbajudContas.return_value = m_api

        object_uuid = uuid4()
        request = RequestFactory().get("v1/sisbajud-contas")
        request.keycloak_token = "12345"
        cpf_solicitante = random_cpf()
        request.user = baker.make(User, username=cpf_solicitante)

        cnpj_entidade = random_cnpj()
        with mock.patch("dataset.views.get_document") as m_get_doc:
            m_get_doc.return_value = cnpj_entidade
            resp = sisbajud_contas(request, object_uuid)

        expected_data = {
            "title": title,
            "description": description,
            "fields": m_SisbajudContas.fields,
            "results": m_api.execute.return_value,
        }
        json_resp = json.loads(resp.content.decode())

        assert resp.status_code == 200
        assert json_resp == expected_data
        m_api.execute.assert_called_once_with(cpf_solicitante, cnpj_entidade, token="12345")

    @mock.patch("dataset.views.SisbajudContas")
    def test_return_error_message_in_any_exception(self, m_SisbajudContas):
        object_uuid = uuid4()
        factory = RequestFactory()
        factory.decoded_token = "xxx"
        request = factory.get("v1/sisbajud-contas")

        m_SisbajudContas.fields = SISBAJUD_CONTAS_FIELDS
        m_SisbajudContas.return_value.execute.side_effect = Exception("Error")
        cnpj_entidade = random_cnpj()
        with mock.patch("dataset.views.get_document") as m_get_doc:
            m_get_doc.return_value = cnpj_entidade
            resp = sisbajud_contas(request, object_uuid)

        json_resp = json.loads(resp.content.decode())

        assert json_resp == {"error": True, "message": "Erro ao obter dados"}


@pytest.mark.django_db
class TestSisbajudOrdensView:
    @override_settings(SISBAJUD_API_URL="http://fakeapi/sisbajud/")
    @mock.patch("dataset.views.get_codigo_tribunal", return_value=42)
    @mock.patch("dataset.views.SisbajudOrdens")
    def test_get_correct_response(self, m_SisbajudOrdens, m_get_codigo_tribunal):
        title = "Sibajud ordens title"
        description = "Sisbajud ordens description"
        baker.make(
            ElementConfig,
            config_type=ElementConfig.CUSTOM_CONFIG,
            name="sisbajud-ordens-title",
            data={"content": title},
        )
        baker.make(
            ElementConfig,
            config_type=ElementConfig.CUSTOM_CONFIG,
            name="sisbajud-ordens-description",
            data={"content": description},
        )

        m_SisbajudOrdens.fields = ["fields"]
        m_SisbajudOrdens.return_value.execute.return_value = ["result"]

        cpf_requisicao = random_cpf()
        request = RequestFactory().get("v1/sisbajud-ordens")
        decoded_token = {"data": []}
        request.decoded_token = decoded_token
        request.user = baker.make(User, username=cpf_requisicao)
        resp = sisbajud_ordens(request)
        expected_data = {
            "title": title,
            "description": description,
            "nome_juiz": format_cpf(cpf_requisicao),
            "results": ["result"],
            "fields": ["fields"],
        }
        json_resp = json.loads(resp.content.decode())

        assert resp.status_code == 200
        assert json_resp == expected_data
        m_SisbajudOrdens.fields = ["fields"]
        m_SisbajudOrdens.return_value.execute.assert_called_once_with(cpf_juiz=cpf_requisicao, cod_tribunal=42)
        m_get_codigo_tribunal.assert_called_once_with(decoded_token, silent=True)

    @override_settings(SISBAJUD_API_URL="http://realapi/sisbajud/")
    @mock.patch("dataset.views.get_codigo_tribunal", return_value=42)
    @mock.patch("dataset.views.SisbajudOrdens")
    def test_get_correct_response_with_cpf_juiz(self, m_SisbajudOrdens, m_get_codigo_tribunal):
        title = "Sibajud ordens title"
        description = "Sisbajud ordens description"
        baker.make(
            ElementConfig,
            config_type=ElementConfig.CUSTOM_CONFIG,
            name="sisbajud-ordens-title",
            data={"content": title},
        )
        baker.make(
            ElementConfig,
            config_type=ElementConfig.CUSTOM_CONFIG,
            name="sisbajud-ordens-description",
            data={"content": description},
        )

        m_SisbajudOrdens.fields = ["fields"]
        m_SisbajudOrdens.return_value.execute.return_value = ["result"]
        cpf_juiz = random_cpf()
        formatted_cpf_juiz = format_cpf(cpf_juiz)
        baker.make(Person, cpf=cpf_juiz, nome="Nome Completo")

        request = RequestFactory().get(f"v1/sisbajud-ordens?cpf={cpf_juiz}")
        decoded_token = {"data": []}
        request.decoded_token = decoded_token
        resp = sisbajud_ordens(request)
        expected_data = {
            "title": title,
            "description": description,
            "nome_juiz": f"Nome Completo ({formatted_cpf_juiz})",
            "results": ["result"],
            "fields": ["fields"],
        }
        json_resp = json.loads(resp.content.decode())

        assert resp.status_code == 200
        assert json_resp == expected_data
        m_SisbajudOrdens.return_value.execute.assert_called_once_with(cpf_juiz=cpf_juiz, cod_tribunal=42)
        m_get_codigo_tribunal.assert_called_once_with(decoded_token, silent=False)

    @mock.patch("dataset.views.SisbajudOrdens")
    def test_return_error_message_in_any_exception(self, m_SisbajudOrdens):
        m_SisbajudOrdens.fields = ["fields"]
        m_SisbajudOrdens.return_value.execute.side_effect = Exception("Error")
        cpf_juiz = random_cpf()
        factory = RequestFactory()
        factory.decoded_token = "xxx"
        request = factory.get(f"v1/sisbajud-ordens?cpf={cpf_juiz}")
        request.user = baker.make(User)
        resp = sisbajud_ordens(request)
        json_resp = json.loads(resp.content.decode())

        expected_simplified = {key: value for key, value in json_resp.items() if key in ("error", "message")}
        assert expected_simplified == {"error": True, "message": "Erro ao obter dados"}


@pytest.mark.django_db
class TestDeclaracaoRendaDetailView:
    @mock.patch("dataset.views.DeclaracaoRenda")
    def test_happy_path_resumo(self, m_DeclaracaoRenda):
        cpf = "123456789"
        ano = "2023"
        m_DeclaracaoRenda.fields = {"fields": "field"}
        m_api = mock.Mock()
        m_api.execute.return_value = {"result": True}
        m_DeclaracaoRenda.return_value = m_api

        request = RequestFactory().get(f"v1/declaracao-renda/{cpf}/{ano}")
        request.keycloak_token = "token"
        resp = declaracao_renda_detalhe(request, cpf, ano)
        json_resp = json.loads(resp.content.decode())
        expected = {"title": "Infojud", "description": "", "fields": {"fields": "field"}, "results": {"result": True}}

        assert resp.status_code == 200
        assert json_resp == expected
        m_api.execute.assert_called_once_with(token="token", cpf_cnpj_entidade=cpf, ano=ano)
