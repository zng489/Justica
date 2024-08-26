from unittest import mock

import responses

from dataset.infojud import DeclaracaoRenda


class TestDeclaracaoRenda:
    @responses.activate
    def test_resumo_declaracao_renda_detalhe(self, dirpf_json):
        api_url = "http://api.com/infojud/"
        token = "token"
        ano = 2022
        cpf = "123456789"
        responses.add(
            responses.GET,
            api_url + f"v1/declaracao-renda/{cpf}/{ano}",
            json=dirpf_json,
            status=200,
        )
        api = DeclaracaoRenda(api_url)

        result = api.execute(token, cpf, ano)
        expected = {
            "ano": 2022,
            "numero_processo": "0000000-00.0000.0.12.34-5",
            "documento": "001.234.567-89",
            "data_recepcao": "6/10/2022",
            "numero_dependentes": 1,
            "fonte_principal": "00.012.345/6780-00",
            "valor_imposto": 12355.39,
            "valor_base_calculo": 500.00,
            "valor_rend_isentos": 100.50,
        }

        assert result["resumo"]["result"] == expected
        assert result["resumo"]["tab_name"] == "Resumo"
        assert result["resumo"]["fields"] == api.fields["resumo"]

    @responses.activate
    def test_bens_declaracao_renda_detalhe(self, dirpf_json):
        api_url = "http://api.com/infojud/"
        token = "token"
        ano = 2022
        cpf = "123456789"
        responses.add(
            responses.GET,
            api_url + f"v1/declaracao-renda/{cpf}/{ano}",
            json=dirpf_json,
            status=200,
        )
        api = DeclaracaoRenda(api_url)

        result = api.execute(token, cpf, ano)
        expected = [
            {
                "tipo": "Veículo",
                "valor_atual": 1000.0,
                "valor_anterior": 900.0,
                "descricao": "Modelo do veículo",
            },
            {
                "tipo": "Ações bolsa de valores",
                "valor_atual": 1545.56,
                "valor_anterior": None,
                "descricao": "Ações do banco",
            },
        ]

        assert result["bens"]["result"] == expected
        assert result["bens"]["fields"] == api.fields["bens"]
        assert result["bens"]["tab_name"] == "Bens e Direitos"
        assert result["bens"]["total"] == 2545.56
        assert result["bens"]["total_anterior"] == 900.00

    @responses.activate
    def test_dependentes_declaracao_renda_detalhe(self, dirpf_json):
        api_url = "http://api.com/infojud/"
        token = "token"
        ano = 2022
        cpf = "123456789"
        responses.add(
            responses.GET,
            api_url + f"v1/declaracao-renda/{cpf}/{ano}",
            json=dirpf_json,
            status=200,
        )
        api = DeclaracaoRenda(api_url)

        with mock.patch("dataset.infojud.uuid_from_document") as m_uuid_from_document:
            m_uuid_from_document.side_effect = [(None, "uuid-1"), (None, "uuid-2")]
            result = api.execute(token, cpf, ano)
        expected = [
            {
                "documento": "001.234.567-89",
                "data_nascimento": "10/10/2015",
                "nome": "Nome Dependente",
                "tipo_dependente": "Tipo dependente",
                "tipo_dependencia": "Tipo dependencia",
                "object_uuid": "uuid-1",
            },
            {
                "documento": "000.876.543-21",
                "data_nascimento": "11/11/2011",
                "nome": "Nome Dependente 2",
                "tipo_dependente": "Tipo dependente 2",
                "tipo_dependencia": "Tipo dependencia 2",
                "object_uuid": "uuid-2",
            },
        ]

        assert result["dependentes"]["fields"] == api.fields["dependentes"]
        assert result["dependentes"]["tab_name"] == "Dependentes"
        assert result["dependentes"]["result"] == expected
        m_uuid_from_document.assert_has_calls([mock.call("123456789"), mock.call("87654321")])

    @responses.activate
    def test_doacoes_declaracao_renda_detalhe(self, dirpf_json):
        api_url = "http://api.com/infojud/"
        token = "token"
        ano = 2022
        cpf = "123456789"
        responses.add(
            responses.GET,
            api_url + f"v1/declaracao-renda/{cpf}/{ano}",
            json=dirpf_json,
            status=200,
        )
        api = DeclaracaoRenda(api_url)

        result = api.execute(token, cpf, ano)
        expected = [
            {
                "tipo_pagamento": "Tipo pagamento",
                "documento_beneficiario": "000.123.456-78",
                "nome_beneficiario": "Nome Beneficiário",
                "doacao_pagamento": "Doação pagamento",
                "nome_dependente": "Nome Dependente",
                "valor": 100.12,
            },
            {
                "tipo_pagamento": "Tipo pagamento 2",
                "documento_beneficiario": "00.000.012/3456-78",
                "nome_beneficiario": "Nome Beneficiário 2",
                "doacao_pagamento": "Doação pagamento 2",
                "nome_dependente": None,
                "valor": 700.00,
            },
        ]

        assert result["doacoes_pagamentos"]["fields"] == api.fields["doacoes_pagamentos"]
        assert result["doacoes_pagamentos"]["tab_name"] == "Doações e Pagamentos"
        assert result["doacoes_pagamentos"]["result"] == expected
        assert result["doacoes_pagamentos"]["total"] == 800.12

    @responses.activate
    def test_rendimentos_declaracao_renda_detalhe(self, dirpf_json):
        api_url = "http://api.com/infojud/"
        token = "token"
        ano = 2022
        cpf = "123456789"
        responses.add(
            responses.GET,
            api_url + f"v1/declaracao-renda/{cpf}/{ano}",
            json=dirpf_json,
            status=200,
        )
        api = DeclaracaoRenda(api_url)

        result = api.execute(token, cpf, ano)
        expected = [
            {
                "tipo_rendimento": "Rendimentos PJ",
                "nome_fonte_pagadora": "Nome fonte pagadora",
                "documento_fonte_pagadora": "00.012.345/6780-00",
                "cpf_beneficiario": "001.234.567-89",
                "descricao": None,
                "valor": 640.00,
            },
            {
                "tipo_rendimento": "Rendimentos PJ",
                "nome_fonte_pagadora": "Nome fonte pagadora 2",
                "documento_fonte_pagadora": "00.087.654/3210-00",
                "cpf_beneficiario": "009.876.543-21",
                "descricao": None,
                "valor": 660.0,
            },
            {
                "tipo_rendimento": "Rendimentos isentos não tributáveis",
                "nome_fonte_pagadora": None,
                "documento_fonte_pagadora": None,
                "cpf_beneficiario": None,
                "descricao": None,
                "valor": 600.0,
            },
            {
                "tipo_rendimento": "Rendimentos isentos",
                "nome_fonte_pagadora": "Nome fonte pagadora",
                "documento_fonte_pagadora": "00.012.345/6780-00",
                "cpf_beneficiario": "001.234.567-89",
                "descricao": "Descrição rendimento",
                "valor": 150.0,
            },
            {
                "tipo_rendimento": "Rendimentos isentos",
                "nome_fonte_pagadora": "Nome fonte pagadora 2",
                "documento_fonte_pagadora": "001.234.567-89",
                "cpf_beneficiario": "001.234.567-89",
                "descricao": "Descrição rendimento 2",
                "valor": 280.0,
            },
            {
                "tipo_rendimento": "Rendimentos recebidos acumuladamente",
                "nome_fonte_pagadora": "Nome fonte pagadora",
                "documento_fonte_pagadora": "00.123.456/7890-00",
                "cpf_beneficiario": None,
                "descricao": None,
                "valor": 42.0,
            },
            {
                "tipo_rendimento": "Rendimentos recebidos acumuladamente",
                "nome_fonte_pagadora": "Nome fonte pagadora 2",
                "documento_fonte_pagadora": "001.234.567-89",
                "cpf_beneficiario": None,
                "descricao": None,
                "valor": 37.0,
            },
            {
                "tipo_rendimento": "Rendimentos com tributação exclusiva na fonte",
                "nome_fonte_pagadora": None,
                "documento_fonte_pagadora": None,
                "cpf_beneficiario": None,
                "descricao": None,
                "valor": 179.00,
            },
            {
                "tipo_rendimento": "Rendimentos com tributação exclusiva na fonte",
                "nome_fonte_pagadora": "Nome fonte pagadora",
                "documento_fonte_pagadora": "00.123.456/7890-00",
                "cpf_beneficiario": "001.234.567-89",
                "descricao": None,
                "valor": 2.00,
            },
            {
                "tipo_rendimento": "Rendimentos com tributação exclusiva na fonte",
                "nome_fonte_pagadora": "Nome fonte pagadora 2",
                "documento_fonte_pagadora": "001.234.567-89",
                "cpf_beneficiario": "001.234.567-89",
                "descricao": None,
                "valor": 100.0,
            },
        ]

        assert result["rendimentos"]["fields"] == api.fields["rendimentos"]
        assert result["rendimentos"]["tab_name"] == "Rendimentos"
        assert result["rendimentos"]["result"] == expected
        assert result["rendimentos"]["total"] == 2690.0
