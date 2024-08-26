import csv
import gzip
import io
import json
import random
from functools import lru_cache
from pathlib import Path

from faker import Faker

faker = Faker("pt-BR")


CNPJ_MULTIPLIERS_1 = tuple(int(x) for x in "543298765432")
CNPJ_MULTIPLIERS_2 = tuple(int(x) for x in "6543298765432")


def classe():
    return random.choice(["120", "199", "278", "39", "66", "7"])


def assuntos():
    n_assuntos = random.randint(0, 10)
    if n_assuntos == 0:
        return None

    choices = [
        {"codigo": 8961, "nome": "Antecipação de Tutela / Tutela Específica"},
        {"codigo": 10076, "nome": "Transporte Terrestre"},
        {"codigo": 11989, "nome": "Nulidade de ato administrativo"},
        {"codigo": 9196, "nome": "Liminar "},
        {"codigo": 3466, "nome": "Atentado Violento ao Pudor "},
        {"codigo": 3490, "nome": "Subtração de Incapazes "},
    ]
    response = []
    for _ in range(n_assuntos):
        item = random.choice(choices)
        if item not in response:
            response.append(item)
    return response


def tribunal():
    return random.choice(["TJPI", "TJSE", "TJRJ", "TJMG", "TJSP", "TJDFT", "TJPE", "STF"])


def vara():
    choices = ["10ª VARA CÍVEL DE BRASÍLIA", "12ª VARA CÍVEL DE BRASÍLIA"]
    return random.choice(choices)


def cpf_checks(text):
    """
    >>> cpf_checks("111111111xx")
    '11'

    >>> cpf_checks("123456789xx")
    '09'
    """
    check_1 = str(((sum(int(c) * (10 - i) for i, c in enumerate(text[:9])) * 10) % 11) % 10)
    check_2 = str(((sum(int(c) * (11 - i) for i, c in enumerate(text[:9] + check_1)) * 10) % 11) % 10)
    return check_1 + check_2


def random_cpf():
    digits = "".join(str(random.randint(0, 9)) for _ in range(9))
    return digits + cpf_checks(digits)


def cnpj_checks(text):
    check_1 = sum(int(c) * m for c, m in zip(text[:12], CNPJ_MULTIPLIERS_1)) % 11
    check_1 = str(11 - check_1 if check_1 >= 2 else 0)
    check_2 = sum(int(c) * m for c, m in zip(text[:12] + check_1, CNPJ_MULTIPLIERS_2)) % 11
    check_2 = str(11 - check_2 if check_2 >= 2 else 0)
    return check_1 + check_2


def random_cnpj():
    digits = "".join(str(random.randint(0, 9)) for _ in range(8)) + "0001"
    return digits + cnpj_checks(digits)


@lru_cache(maxsize=1)
def read_person_list():
    path = Path("./source/person.csv.gz")
    fobj = io.TextIOWrapper(gzip.GzipFile(path), encoding="utf-8")
    return list(csv.DictReader(fobj))


@lru_cache(maxsize=1)
def read_company_list():
    path = Path("./source/company.csv.gz")
    fobj = io.TextIOWrapper(gzip.GzipFile(path), encoding="utf-8")
    return list(csv.DictReader(fobj))


def documento():
    if random.random() > 0.5:  # CPF
        obj = random.choice(read_person_list())
        return obj["cpf"], obj["nome"]
    else:  # CNPJ
        obj = random.choice(read_company_list())
        return obj["cnpj"], obj["razao_social"]


def valor():
    if random.random() > 0.8:
        return None
    else:
        centavos = str(random.random())[2:4]
        return float(f"{random.randint(10, 10000)}.{centavos}")


def numero_processo():
    return "".join([str(random.randint(0, 10)) for _ in range(20)])


def nome():
    return faker.name()


def empresa():
    return faker.company()


def random_bool(threshold: float):
    return random.random() > threshold


def numero_conta():
    return "{}{}{}{}{}-{}".format(*[random.randint(0, 9) for _ in range(6)])


def numero_agencia():
    return "{}{}{}{}{}".format(*[random.randint(0, 9) for _ in range(5)])


def contas(n):
    bancos = [
        ("AGILLITAS SOLUÇÕES DE PAGAMENTOS LTDA", "42886", "13.776.742/0001-55"),
        ("AME DIGITAL BRASIL IP LTDA.", "00040", "32.778.350/0001-70"),
        ("BANCO BS2 S.A.", "05218", "71.027.866/0001-34"),
        ("BCO BRADESCO", "05237", "60.746.948/0001-12"),
        ("BCO BRASIL", "00001", "00.000.000/0001-91"),
        ("BCO BTG PACTUAL", "05208", "30.306.294/0001-45"),
        ("BCO C6 S.A.", "42122", "31.872.495/0001-72"),
        ("BCO MODAL", "05746", "30.723.886/0001-62"),
        ("BCO SANTANDER", "03008", "90.400.888/0001-42"),
        ("BCO VOTORANTIM", "05655", "59.588.111/0001-03"),
        ("BEXS BCO DE CAMBIO S.A.", "28866", "13.059.145/0001-00"),
        ("BNY MELLON BANCO S.A.", "29536", "42.272.526/0001-70"),
        ("BS2 DTVM S.A.", "40953", "28.650.236/0001-92"),
        ("CAIXA ECONOMICA FEDERAL", "21104", "00.360.305/0001-04"),
        ("CC EMP GRANDE CTBA E C. GERAIS", "18246", "05.888.589/0001-20"),
        ("COIN-DISTRIBUIDORA DE TITULOS E VALORES MOBILIARIOS LTDA", "57346", "61.384.004/0001-05"),
        ("EASYNVEST - TÍTULO CV SA", "57237", "62.169.875/0001-79"),
        ("GENIAL INVESTIMENTOS CORRETORA DE VALORES MOBILIÁRIOS S.A.", "57487", "27.652.684/0001-62"),
        ("ITAÚ UNIBANCO S.A. ", "07341", "60.701.190/0001-04"),
        ("MERCADOPAGO.COM REPRESENTACOES LTDA.", "42300", "10.573.521/0001-91"),
        ("MODAL DTVM", "16921", "05.389.174/0001-01"),
        ("NEON PAGAMENTOS S.A.", "44368", "20.855.875/0001-82"),
        ("NU PAGAMENTOS S.A.", "40923", "18.236.120/0001-58"),
        ("PAGSEGURO INTERNET S.A.", "40989", "08.561.701/0001-01"),
        ("PAYPAL DO BRASIL SERVICOS DE PAGAMENTOS LTDA.", "42644", "10.878.448/0001-66"),
        ("PICPAY INSTITUIÇÃO DE PAGAMENTO S.A.", "43281", "22.896.431/0001-10"),
        ("TORO CTVM LTDA", "41265", "29.162.769/0001-98"),
        ("WARREN CORRETORA DE VALORES MOBILIÁRIOS E CÂMBIO LTDA.", "57199", "92.875.780/0001-31"),
        ("XP INVESTIMENTOS CCTVM S/A", "08844", "02.332.886/0001-04"),
        ("ÓRAMA DTVM S.A.", "29041", "13.293.225/0001-25"),
    ]
    random.shuffle(bancos)
    result = []

    for _ in range(n):
        razao_social, codigo, cnpj = bancos.pop(0)
        result.append(
            {
                "nomeInstituicaoFinanceira": razao_social,
                "cnpjInstituicaoFinanceira": cnpj,
                "agencia": numero_agencia() if random.randint(0, 10) > 9 else None,
                "numeroConta": numero_conta() if random.randint(0, 10) > 9 else None,
                "codigoInstituicaoFinanceira": codigo,
                "ativo": random_bool(0.5),
            }
        )
    return result


def pessoa():
    document, name = documento()
    return {"pessoa": {"nome": name, "documento": document}}


def partes():
    n_partes = random.randint(0, 3)
    if n_partes == 0:
        return None

    response = []
    for _ in range(n_partes):
        response.append(
            {
                **pessoa(),
                "advogados": [pessoa() for _ in range(random.randint(0, 2))],
            }
        )
    return response


def nivel_sigilo():
    return random.choice([0, None])


def movimento():
    if random.randint(0, 10) == 0:
        return None

    choices = [
        {"codigo": 11010, "dataHora": 20221129051656},
        {"codigo": 11383, "dataHora": 20221020082712},
        {"codigo": 132, "dataHora": 20201220201314},
        {"codigo": 22, "dataHora": 20211119074058},
        {"codigo": 246, "dataHora": 20200115094139},
    ]
    return random.choice(choices)


def orgao_julgador():
    if random.randint(0, 10) == 0:
        return None

    choices = [
        {"id": 27845, "nome": "GABINETE DES. OSÓRIO DE ARAÚJO RAMOS FILHO"},
        {"id": 27846, "nome": "GABINETE DES. EDSON ULISSES DE MELO"},
        {"id": 27848, "nome": "GABINETE DES. JOSÉ DOS ANJOS"},
        {"id": 6996, "nome": "JECC TERESINA - ZONA NORTE 2 - SEDE (BUENOS AIRES)"},
        {"id": 8328, "nome": "3 ª VARA CÍVEL DE ARACAJU"},
        {"id": 8343, "nome": "18 ª VARA CÍVEL DE ARACAJU"},
        {"id": 8588, "nome": "1 ª CÍVEL E CRIMINAL DE NEÓPOLIS"},
    ]
    return random.choice(choices)


def parte_ordens():
    document, name = documento()
    return {
        "nomeExecutado": name,
        "cpfCnpjExecutado": document,
        "valorAplicado": valor(),
    }


def protocolo():
    return "{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(*[random.randint(0, 9) for _ in range(14)])


def codigo_processo():
    return "{}{}{}{}{}{}{}-{}{}.{}{}{}{}.{}.{}{}.{}{}{}{}".format(*[random.randint(0, 9) for _ in range(20)])


def data_protocolamento():
    return str(faker.past_datetime(start_date="-10y"))


def descricao_situacao():
    choices = ["Respondida"]
    return random.choice(choices)


def cabecalho_processual(documento):
    n_results = random.randint(0, 6)
    if n_results == 0 or documento == "83648294164":
        return {
            "code": 404,
            "messages": ["Ocorreu um erro inesperado: Processo(s) não encontrado(s) "],
            "result": None,
            "status": "error",
        }

    response = {
        "code": 10,
        "messages": None,
        "page-info": {
            "count": 2,
            "current": 1,
            "last": 1,
            "size": 10,
        },
        "status": "200 OK",
        "result": [],
    }
    for _ in range(n_results):
        response["result"].append(
            {
                "numeroProcesso": numero_processo(),
                "classeProcessual": classe(),
                "siglaTribunal": tribunal(),
                "assuntos": assuntos(),
                "partes": partes(),
                "orgaoJulgador": orgao_julgador(),
                "nivelSigilo": nivel_sigilo(),
                "ultimoMovimento": movimento(),
            }
        )

    return response


def sisbajud_contas(cpf):
    has_contas = random.random() <= 0.9
    n_contas = random.randint(3, 10) if has_contas else 0
    return {
        "nomeExecutado": nome().upper(),
        "contas": contas(n_contas),
    }


def tipo_ordem_sisbajud():
    return random.choice(
        [
            "Bloqueio de valores",
            "Requisição de informações",
            "Extrados e demais informações",
        ]
    )


def sisbajud_ordens(cpf_juiz):
    n_ordens = random.randint(3, 6)
    content = []
    for _ in range(n_ordens):
        n_partes = random.randint(2, 3)
        content.append(
            {
                "protocolo": protocolo(),
                "codProcesso": codigo_processo(),
                "dataHoraProtocolamento": data_protocolamento(),
                "descricaoTipoOrdem": tipo_ordem_sisbajud(),
                "descricaoSituacao": descricao_situacao(),
                "nomeJuiz": nome().upper(),
                "nomeAssessor": nome().upper(),
                "nomeTribunal": tribunal(),
                "varaJuizo": vara(),
                "listaReus": [parte_ordens() for _ in range(n_partes)],
            }
        )

    return {"content": content}


def declaracao_renda_lista():
    result = []
    for _ in range(4):
        document, name = documento()
        result.append({"nome": name, "documento": document, "numero_processo": codigo_processo()})

    return result


def declaracao_renda_detalhe(cpf_cnpj_entidade, ano):
    dirpf_path = Path("./source/DIRPF.json.gz")
    dirprf = io.TextIOWrapper(gzip.GzipFile(dirpf_path), encoding="utf-8")
    return json.load(dirprf)


def declaracao_renda_detalhe_pj(cpf_cnpj_entidade, ano):
    dirpf_path = Path("./source/efin_completo.json.gz")
    dirprf = io.TextIOWrapper(gzip.GzipFile(dirpf_path), encoding="utf-8")
    return json.load(dirprf)
