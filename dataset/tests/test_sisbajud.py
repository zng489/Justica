from urllib.parse import urljoin

import responses

from dataset.sisbajud import SisbajudContas


class TestSisbajudContas:
    @responses.activate
    def test_happy_path(self):
        api_url = "http://fakeapi/sisbajud/"
        json_data = {
            "contas": [
                {
                    "codigoInstituicaoFinanceira": "1111",
                    "nomeInstituicaoFinanceira": "Banco Um",
                    "cnpjInstituicaoFinanceira": "11111111",
                    "instituicaoFinanceiraAtiva": True,
                    "numeroConta": "12345",
                    "agencia": "12345",
                    "contaUnica": False,
                    "relacionamentoCCS": True,
                    "ativo": False,
                    "lider": True,
                    "instituicaoLider": None,
                },
                {
                    "codigoInstituicaoFinanceira": "2222",
                    "nomeInstituicaoFinanceira": "Banco Dois",
                    "cnpjInstituicaoFinanceira": "22222222",
                    "instituicaoFinanceiraAtiva": True,
                    "numeroConta": "54321",
                    "agencia": "54321",
                    "contaUnica": False,
                    "relacionamentoCCS": True,
                    "ativo": True,
                    "lider": True,
                    "instituicaoLider": None,
                },
                {
                    "codigoInstituicaoFinanceira": None,
                    "nomeInstituicaoFinanceira": "Banco Três",
                    "cnpjInstituicaoFinanceira": "33333333",
                    "instituicaoFinanceiraAtiva": True,
                    "numeroConta": "54321",
                    "agencia": "54321",
                    "contaUnica": False,
                    "relacionamentoCCS": True,
                    "ativo": True,
                    "lider": True,
                    "instituicaoLider": None,
                },
                {
                    "codigoInstituicaoFinanceira": "4444",
                    "nomeInstituicaoFinanceira": "Banco Quatro",
                    "cnpjInstituicaoFinanceira": "12345678901234",
                    "instituicaoFinanceiraAtiva": True,
                    "numeroConta": "54321",
                    "agencia": "54321",
                    "contaUnica": False,
                    "relacionamentoCCS": True,
                    "ativo": True,
                    "lider": True,
                    "instituicaoLider": None,
                },
                {
                    "codigoInstituicaoFinanceira": None,
                    "nomeInstituicaoFinanceira": None,
                    "cnpjInstituicaoFinanceira": None,
                    "instituicaoFinanceiraAtiva": True,
                    "numeroConta": "54321",
                    "agencia": "54321",
                    "contaUnica": False,
                    "relacionamentoCCS": True,
                    "ativo": True,
                    "lider": True,
                    "instituicaoLider": None,
                },
            ]
        }

        cpf = "1111"
        cnpj = "22222"
        responses.add(
            responses.GET,
            urljoin(api_url, f"/sisbajud/v1/relacionamento/{cnpj}") + f"?cpfUsuarioSolicitante={cpf}",
            status=200,
            json=json_data,
        )

        api = SisbajudContas(api_url)
        result = api.execute(cpf_solicitante=cpf, cpf_cnpj_entidade=cnpj, token="token")
        expected_result = [
            ["Banco Um (1111)", "11.111.111/0001-91", False],
            ["Banco Dois (2222)", "22.222.222/0001-91", True],
            ["Banco Três", "33.333.333/0001-91", True],
            ["Banco Quatro (4444)", "12.345.678/9012-34", True],
            [None, None, True],
        ]

        assert result == expected_result
