import pytest


@pytest.fixture
def dirpf_resumo_json():
    cnpj = "12345678000"
    return {
        "dataRecepcao": {"ano": 2022, "dia": 6, "mes": 10},
        "valorImposto": 12355.39,
        "numeroDependentes": 1,
        "valorBaseCalculo": 500.00,
        "valorRendIsentos": 100.50,
        "numeroInscricaoFontePrincipal": {"isCpf": False, "codigo": cnpj, "isCnpj": True},
    }


@pytest.fixture
def dirpf_bens_json():
    return [
        {
            "bemDireito": "Veículo",
            "valorAtual": 1000.0,
            "valorAnterior": 900.0,
            "descricaoBemParte1": "Modelo do veículo",
        },
        {
            "bemDireito": "Ações bolsa de valores",
            "valorAtual": 1545.56,
            "valorAnterior": None,
            "descricaoBemParte1": "Ações do banco",
        },
    ]


@pytest.fixture
def dirpf_dependentes_json():
    return [
        {
            "cpfDependente": {"cpf": "123456789"},
            "dataNascimento": {"ano": 2015, "mes": 10, "dia": 10},
            "nomeDependente": "Nome Dependente",
            "tipoDependente": "Tipo dependente",
            "tipoDependencia": "Tipo dependencia",
        },
        {
            "cpfDependente": {"cpf": "87654321"},
            "dataNascimento": {"ano": 2011, "mes": 11, "dia": 11},
            "nomeDependente": "Nome Dependente 2",
            "tipoDependente": "Tipo dependente 2",
            "tipoDependencia": "Tipo dependencia 2",
        },
    ]


@pytest.fixture
def dirpf_doacoes_json():
    return [
        {
            "tipoPagamento": "Tipo pagamento",
            "niBeneficiario": {"isCpf": True, "codigo": "12345678"},
            "nomeDependente": "Nome Dependente",
            "doacaoPagamento": "Doação pagamento",
            "nomeBeneficiario": "Nome Beneficiário",
            "valorDoacaoPagamento": 100.12,
        },
        {
            "tipoPagamento": "Tipo pagamento 2",
            "niBeneficiario": {"isCpf": False, "codigo": "12345678", "isCnpj": True},
            "doacaoPagamento": "Doação pagamento 2",
            "nomeBeneficiario": "Nome Beneficiário 2",
            "valorDoacaoPagamento": 700.00,
        },
    ]


@pytest.fixture
def dirpf_rendimentos_json():
    return {
        "rendimentosPJ": [
            {
                "valorRenda": 100.0,
                "cpfBeneficiario": {"cpf": "123456789"},
                "cnpjFontePagadora": {"cnpj": "12345678000"},
                "nomeFontePagadora": "Nome fonte pagadora",
                "valorDecimoTercSalario": 120.0,
                "valorContribPrevOficial": 130.0,
                "valorImpostoRetidoFonte": 140.0,
                "valorImpostoRetidoFonteDecimoTerceiro": 150.0,
            },
            {
                "valorRenda": 200.0,
                "cpfBeneficiario": {"cpf": "987654321"},
                "cnpjFontePagadora": {"cnpj": "87654321000"},
                "nomeFontePagadora": "Nome fonte pagadora 2",
                "valorDecimoTercSalario": 220.0,
                "valorContribPrevOficial": None,
                "valorImpostoRetidoFonte": 240.0,
                "valorImpostoRetidoFonteDecimoTerceiro": None,
            },
        ],
        "rendimentosIsentosNT": {
            "valorPeculio": 100.0,
            "valorPoupanca": 200.0,
            "valorBolsaEstudo": 300.0,
            # ...
        },
        "rendimentosIsentosDetalhes": [
            {
                "fontePagadora": {"isCpf": False, "codigo": "12345678000", "isCnpj": True},
                "cpfBeneficiario": {"cpf": "123456789"},
                "nomeFontePagadora": "Nome fonte pagadora",
                "descricaoRendimento": "Descrição rendimento",
                "valorGanhoCapital": 100.0,
                "valorDecimoTerceiroSalario": 0.0,
                "valorImpostoRendaRetidoFonte": None,
                "valorImpostoRendaRetidoFonteDecimoTerceiroSalario": 50.0,
            },
            {
                "fontePagadora": {"isCpf": True, "codigo": "123456789", "isCnpj": False},
                "cpfBeneficiario": {"cpf": "123456789"},
                "nomeFontePagadora": "Nome fonte pagadora 2",
                "descricaoRendimento": "Descrição rendimento 2",
                "valorGanhoCapital": 200.0,
                "valorDecimoTerceiroSalario": None,
                "valorImpostoRendaRetidoFonte": 30.0,
                "valorImpostoRendaRetidoFonteDecimoTerceiroSalario": 50.0,
            },
        ],
        "rendimentosRecebidosAcumuladamente": [
            {
                "niFontePagadora": {"isCpf": False, "codigo": "123456789000", "isCnpj": True},
                "valorImpostoRRA": 5.0,
                "nomeFontePagadora": "Nome fonte pagadora",
                "valorPensaoAlimenticia": 10.0,
                "valorPrevidenciaOficial": 15.0,
                "valorRendimentoRecebido": 12.0,
            },
            {
                "niFontePagadora": {"isCpf": True, "codigo": "123456789", "isCnpj": False},
                "valorImpostoRRA": None,
                "nomeFontePagadora": "Nome fonte pagadora 2",
                "valorPensaoAlimenticia": 10.0,
                "valorPrevidenciaOficial": 15.0,
                "valorRendimentoRecebido": 12.0,
            },
        ],
        "rendimentosTributacaoExclusivaFonte": {
            "valorRRA": 45.0,
            "valorRRADep": 0,
            "valor13Salario": 134.00,
            # ...
        },
        "rendimentosTributacaoExclusivaFonteDetalhes": [
            {
                "cpfBeneficiario": {"cpf": "123456789"},
                "niFontePagadora": {"isCpf": False, "codigo": "123456789000", "isCnpj": True},
                "valorRecebimento": 2.0,
                "nomeFontePagadora": "Nome fonte pagadora",
            },
            {
                "cpfBeneficiario": {"cpf": "123456789"},
                "niFontePagadora": {"isCpf": True, "codigo": "123456789", "isCnpj": False},
                "valorRecebimento": 100.0,
                "nomeFontePagadora": "Nome fonte pagadora 2",
            },
        ],
    }


@pytest.fixture
def dirpf_json(dirpf_resumo_json, dirpf_bens_json, dirpf_dependentes_json, dirpf_doacoes_json, dirpf_rendimentos_json):
    dirpf_json = [
        {
            "ano": 2022,
            "numeroProcesso": "1234-5",
            "cpfCnpj": "123456789",
            "dirpf": [dict()],
        },
    ]
    dirpf_json[0]["dirpf"][0]["resumo"] = dirpf_resumo_json
    dirpf_json[0]["dirpf"][0]["bensDireitos"] = dirpf_bens_json
    dirpf_json[0]["dirpf"][0]["dependentes"] = dirpf_dependentes_json
    dirpf_json[0]["dirpf"][0]["doacoesPagamentos"] = dirpf_doacoes_json
    dirpf_json[0]["dirpf"][0]["rendimentos"] = dirpf_rendimentos_json
    return dirpf_json
