import csv
import datetime
import json
import random
import uuid

import rows
from django.conf import settings
from django.core.management.base import BaseCommand
from tqdm import tqdm

from dataset import choices

FAKE_DATA_PATH = settings.BASE_DIR / "fake-data"
paises = [item[1] for item in choices.PAIS]
TIPO_SOCIO = [(1, "Pessoa jurídica"), (2, "Pessoa física")]
totalizacoes_turno = (
    "",
    "ELEITO POR QP",
    "ELEITO",
    "NAO ELEITO",
    "2O TURNO",
    "ELEITO POR MEDIA",
    "SUPLENTE",
)
logradouros = (
    "9 DE JULHO",
    "ANITA GARIBALDI",
    "AUGUSTO STRESSER",
    "BARÃO DE MAUA",
    "BENTO GONÇALVES",
    "BENTO ROSA",
    "BRIGADEIRO FARIA LIMA",
    "DAS ACACIAS",
    "DESEMBARGADOR FELINTO BASTOS",
    "DOS OPERARIOS",
    "GUAPORE",
    "MARECHAL DEODORO",
    "MONSENHOR ANDRADE",
    "RIO BRANCO",
    "SAO JOAO",
    "SAO VICENTE DE PAULO",
    "SETE DE SETEMBRO",
    "XV DE NOVEMBRO",
)
situacoes_especiais = (
    "EM LIQUIDACAO",
    "ESPOLIO EV 407",
    "FALIDO",
    "INTERVENCAO",
    "LIQUIDACAO EXTRA-JUDICIAL",
    "LIQUIDACAO JUDICIAL",
    "RECUPERACAO JUDICIAL",
)
siglas_partidos = (
    "PHS",
    "PCO",
    "PTC",
    "PTN",
    "PATRIOTA",
    "REDE",
    "PPS",
    "PPL",
    "DEM",
    "PMN",
    "PSB",
    "PR",
    "PP",
    "MDB",
    "PRB",
    "SOLIDARIEDADE",
    "PV",
    "UNIAO",
    "DC",
    "PRP",
    "PRTB",
    "REPUBLICANOS",
    "AVANTE",
    "SD",
    "PT DO B",
    "CIDADANIA",
    "PODE",
    "PROS",
    "PC DO B",
    "PL",
    "PSL",
    "NOVO",
    "PSTU",
    "UP",
    "PSDB",
    "PT",
    "PMB",
    "PDT",
    "PSD",
    "PSC",
    "PCB",
    "PTB",
    "PSDC",
    "PSOL",
    "PMDB",
)
cargos = (
    "VICE-PREFEITO",
    "VEREADOR",
    "VICE-PRESIDENTE",
    "1o SUPLENTE SENADOR",
    "DEPUTADO FEDERAL",
    "SENADOR",
    "2o SUPLENTE SENADOR",
    "VICE-GOVERNADOR",
    "DEPUTADO ESTADUAL",
    "DEPUTADO DISTRITAL",
    "PRESIDENTE",
    "PREFEITO",
    "GOVERNADOR",
)


def read_values(filename):
    with open(FAKE_DATA_PATH / filename) as fobj:
        return [row["valor"] for row in csv.DictReader(fobj)]


cidades_exteriores = read_values("cidade_exterior.csv")
tipos_logradouro = read_values("tipo_logradouro.csv")
tipo_empresa = read_values("tipo_empresa.csv")
sobrenomes = read_values("sobrenome.csv")
nomes = read_values("nome.csv")
nomes_femininos = read_values("nome_feminino.csv")
with open(FAKE_DATA_PATH / "populacao-por-municipio-2020.csv") as fobj:
    municipios = list(csv.DictReader(fobj))
    ufs = list(set(row["state"] for row in municipios))


CNPJ_MULTIPLIERS_1 = tuple(int(x) for x in "543298765432")
CNPJ_MULTIPLIERS_2 = tuple(int(x) for x in "6543298765432")


def cnpj_checks(text):
    check_1 = sum(int(c) * m for c, m in zip(text[:12], CNPJ_MULTIPLIERS_1)) % 11
    check_1 = str(11 - check_1 if check_1 >= 2 else 0)
    check_2 = sum(int(c) * m for c, m in zip(text[:12] + check_1, CNPJ_MULTIPLIERS_2)) % 11
    check_2 = str(11 - check_2 if check_2 >= 2 else 0)
    return check_1 + check_2


def random_ano_obito():
    if random.randint(0, 100) < 15:
        return random.randint(1960, 2022)
    return None


def random_ano_eleicao():
    return random.choice([2014, 2016, 2018, 2020])


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


def random_nome():
    nome = random.choice(nomes)
    if random.randint(0, 100) < 5:
        nome += f" {random.choice(nomes)}"
    for _ in range(random.randint(1, 4)):
        nome += f" {random.choice(sobrenomes)}"
    return nome


def random_nome_urna():
    nome = random.choice(nomes)
    if random.randint(0, 100) < 5:
        nome = f"BOMBEIRO {nome}"
    elif random.randint(0, 100) < 5:
        nome = f"PROFESSOR {nome}"
    else:
        nome = f"{nome} DO {random.choice(tipo_empresa)}"
    return nome


def random_nome_feminino():
    nome = random.choice(nomes_femininos)
    if random.randint(0, 100) < 5:
        nome += f" {random.choice(nomes_femininos)}"
    for _ in range(random.randint(1, 4)):
        nome += f" {random.choice(sobrenomes)}"
    return nome


def random_nome_social():
    if random.randint(0, 100) < 2:
        return random_nome()
    return None


def random_razao_social():
    razao_social = f"{random.choice(tipo_empresa)} {random.choice(nomes)} {random.choice(sobrenomes)}"
    razao_social += " " + random.choice(["LTDA", "ME", "S.A."])
    return razao_social


def random_nome_fantasia():
    return f"{random.choice(tipo_empresa)} {random.choice(nomes)} {random.choice(sobrenomes)}"


def random_cpf():
    digits = "".join(str(random.randint(0, 9)) for _ in range(9))
    return digits + cpf_checks(digits)


def random_cpf_responsavel():
    if random.randint(0, 100) < 10:
        return random_cpf()
    return None


def random_cnpj():
    digits = "".join(str(random.randint(0, 9)) for _ in range(8)) + "0001"
    return digits + cnpj_checks(digits)


def random_titulo_eleitoral():
    # TODO: create checks using algorithm
    return "".join(str(random.randint(0, 9)) for _ in range(12))


def random_datetime():
    year = random.randint(1900, 2022)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour = random.randint(1, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime.datetime(year, month, day, hour, minute, second)


def random_date():
    year = random.randint(1900, 2022)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime.date(year, month, day)


def random_data_nascimento():
    year = random.randint(1900, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime.date(year, month, day)


def random_integer(choices=None, min_value=None, max_value=None):
    if choices is not None:
        return random.choice(choices)
    elif max_value is not None and min_value is not None:
        return random.randint(min_value, max_value)
    else:
        raise ValueError(
            f"Missing correct configs for random_integer: choices={choices}, min_value={min_value}, max_value={max_value}"
        )


def random_text(choices=None):
    if choices is not None:
        return random.choice(choices)
    else:
        raise ValueError(f"Missing correct configs for random_text: choices={choices}")


def generate_row(fields):
    row = {}
    for field_name, configs in fields.items():
        if configs["type"] == "uuid":
            value = uuid.uuid4()

        elif configs["type"] == "date":
            value = random_date()

        elif configs["type"] == "datetime":
            value = random_datetime()

        elif configs["type"] == "integer":
            value = random_integer(
                choices=configs.get("choices"),
                min_value=configs.get("min"),
                max_value=configs.get("max"),
            )

        elif configs["type"] == "func":
            value = configs["func"]()

        elif configs["type"] == "text":
            value = random_text(choices=configs.get("choices"))

        row[field_name] = value
    return row


def random_email():
    username = random.choice(nomes) + random.choice(["_", ".", ""]) + random.choice(sobrenomes)
    domain = random.choice(["gmail.com", "hotmail.com", "uol.com.br", "terra.com.br"])
    return f"{username}@{domain}".lower()


def random_cnae_multiple():
    options = [str(item[0]) for item in choices.EMPRESA_CNAE]
    return "{" + ",".join([random.choice(options) for _ in range(2)]) + "}"


def random_city():
    city = random.choice(municipios)
    return city["city"], city["state"]


def random_cep():
    if random.randint(0, 100) > 10:
        return random_integer(min_value=10_000_000, max_value=99_999_999)
    return None


def random_telefone():
    return f"{random.randint(11, 99)} 9{random.randint(0,9999):04d}-{random.randint(0,9999):04d}"


def random_endereco():
    tipo = random.choice(tipos_logradouro)
    logradouro = random.choice(logradouros)
    numero = random.randint(10, 999)
    endereco = f"{tipo} {logradouro}, {numero}"
    if random.randint(0, 100) < 50:
        endereco += f" (ap. {random.randint(21, 99)})"
    endereco += " - Centro"
    return endereco


def create_person():
    row = {
        "updated_at": random_datetime(),
        "data_atualizacao": random_date(),
        "nome": random_nome(),
        "nome_social": random_nome_social(),
        "cpf": random_cpf(),
        "sexo": random_text(choices=("M", "F")),
        "titulo_eleitoral": random_titulo_eleitoral(),
        "data_nascimento": random_data_nascimento(),
        "nome_mae": random_nome_feminino(),
        "ano_obito": random_ano_obito(),
        "residente_exterior": random_text(choices=("t", "f")),
        "codigo_natureza_ocupacao": random_integer(
            choices=[item[0] for item in choices.PESSOA_FISICA_NATUREZA_OCUPACAO]
        ),
        "codigo_ocupacao_principal": random_integer(
            choices=[item[0] for item in choices.PESSOA_FISICA_OCUPACAO_PRINCIPAL]
        ),
        "ano_exercicio_ocupacao": random_integer(min_value=2000, max_value=2022),
        "cep": random_cep(),
        "telefone": random_telefone() if random.randint(0, 100) < 80 else None,
        "endereco": random_endereco(),
    }
    row["object_uuid"] = uuid.uuid5(uuid.NAMESPACE_URL, f"https://id.sniper.pdpj.jus.br/person/v1/{row['cpf']}/")
    row["data_inscricao"] = row["data_nascimento"] + datetime.timedelta(days=365 * random.randint(1, 18))

    if random.randint(0, 100) < 10:
        row["codigo_situacao_cadastral"] = random_integer(
            choices=[item[0] for item in choices.PESSOA_FISICA_SITUACAO_CADASTRAL]
        )
    else:
        row["codigo_situacao_cadastral"] = 0  # Ativa

    row["municipio"], row["uf"] = random_city()
    if random.randint(0, 100) < 30:
        row["municipio_nascimento"], row["uf_nascimento"] = random_city()
    else:
        row["municipio_nascimento"], row["uf_nascimento"] = row["municipio"], row["uf"]

    row["pais_exterior"] = None
    row["pais_nacionalidade"] = None
    if random.randint(0, 100) < 3:
        row["pais_exterior"] = random.choice(paises)
        row["pais_nacionalidade"] = random.choice(paises)

    return {
        "object_uuid": row.pop("object_uuid"),
        "updated_at": row.pop("updated_at"),
        **row,
    }


def create_company():
    row = {
        "updated_at": random_datetime(),
        "cnpj": random_cnpj(),
        "razao_social": random_razao_social(),
        "nome_fantasia": random_nome_fantasia(),
        "cnae": random_cnae_multiple(),
        "data_cadastro": random_date(),
        "data_situacao_cadastral": random_date(),
        "codigo_natureza_juridica": random_integer(choices=[item[0] for item in choices.EMPRESA_NATUREZA_JURIDICA]),
        "codigo_porte": random_integer(choices=[item[0] for item in choices.EMPRESA_PORTE]),
        "capital_social": random_integer(min_value=100, max_value=15000000),
        "opcao_simples": random_text(choices=["t", "f"]),
        "opcao_mei": random_text(choices=["t", "f"]),
        "codigo_qualificacao_responsavel": random_qualificacao(),
        "cpf_responsavel": random_cpf_responsavel(),
        "email": random_email(),
        "codigo_municipio": random_integer(min_value=1, max_value=9997),
        "uf": random.choice(ufs),
        "cep": random_cep(),
        "telefone_1": random_telefone(),
        "endereco": random_endereco(),
    }
    row["object_uuid"] = uuid.uuid5(uuid.NAMESPACE_URL, f"https://id.brasil.io/company/v1/{row['cnpj'][:8]}/")

    if random.randint(0, 100) < 20:
        row["codigo_situacao_cadastral"] = random_integer(
            choices=[item[0] for item in choices.EMPRESA_SITUACAO_CADASTRAL]
        )
        row["codigo_motivo_situacao_cadastral"] = random_integer(
            choices=[item[0] for item in choices.EMPRESA_MOTIVO_SITUACAO_CADASTRAL]
        )
    else:
        row["codigo_situacao_cadastral"] = 2  # Ativa
        row["codigo_motivo_situacao_cadastral"] = None

    row["telefone_2"] = None
    if random.randint(0, 100) < 15:
        row["telefone_2"] = random_telefone()

    row["cidade_exterior"], row["codigo_pais"] = None, None
    if random.randint(0, 100) == 0:
        row["codigo_pais"] = random.choice([item[0] for item in choices.PAIS])
        row["cidade_exterior"] = random.choice(cidades_exteriores)

    row["situacao_especial"] = None
    row["data_situacao_especial"] = None
    if random.randint(0, 100) < 5:
        row["situacao_especial"] = random.choice(situacoes_especiais)
        row["data_situacao_especial"] = random_date()

    return {
        "object_uuid": row.pop("object_uuid"),
        "updated_at": row.pop("updated_at"),
        **row,
    }


def create_candidacy():
    row = {
        "updated_at": random_datetime(),
        "ano": random_ano_eleicao(),
        "cargo": random.choice(cargos),
        "nome_urna": random_nome_urna(),
        "numero_sequencial": random_integer(min_value=100_000_000_000_000, max_value=999_999_999_999_999),
        "sigla_partido": random.choice(siglas_partidos),
        "sigla_unidade_federativa": random.choice(ufs),
        "totalizacao_turno": random.choice(totalizacoes_turno),
    }
    if random.randint(0, 100) < 1:
        row["unidade_eleitoral"] = "BR"
    elif random.randint(0, 100) < 10:
        row["unidade_eleitoral"] = row["sigla_unidade_federativa"]
    else:
        row["unidade_eleitoral"], row["sigla_unidade_federativa"] = random_city()

    row["object_uuid"] = uuid.uuid5(
        uuid.NAMESPACE_URL, f"https://id.brasil.io/candidacy/v1/{row['ano']}-{row['numero_sequencial']}/"
    )
    return {
        "object_uuid": row.pop("object_uuid"),
        "updated_at": row.pop("updated_at"),
        **row,
    }


def random_qualificacao():
    # return random_integer(choices=[item[0] for item in choices.EMPRESA_QUALIFICACAO_SOCIO if item[0] <= 28])
    return random_integer(choices=[item[0] for item in choices.EMPRESA_QUALIFICACAO_SOCIO])


def random_cnpj_raiz_multiple():
    return ["".join(str(random.randint(0, 9)) for __ in range(8)) for _ in range(3)]


def random_codigo_multiple():
    return [random_qualificacao() for _ in range(3)]


runs_for_fields = {}
is_partner_fields = {
    "codigo_qualificacao": {"type": "func", "func": random_qualificacao},
    "codigo_qualificacao_representante": {"type": "func", "func": random_qualificacao},
    "cpf_representante_legal": {"type": "func", "func": random_cpf_responsavel},
    "data_entrada_sociedade": {"type": "date"},
    "codigo_pais": {"type": "integer", "choices": [item[0] for item in choices.PAIS]},
    "codigo_tipo_socio": {"type": "integer", "choices": [item[0] for item in TIPO_SOCIO]},
}
represents_fields = {
    "cnpj_raiz": {"type": "func", "func": random_cnpj_raiz_multiple},
    "codigo_qualificacao_representante": {"type": "func", "func": random_codigo_multiple},
}
bemdeclarado_fields = {
    "tipo": {"type": "text", "choices": [item[0] for item in choices.BEM_DECLARADO_TIPO]},
    "valor": {"type": "integer", "min": 100, "max": 15000000},
    "descricao": {"type": "func", "func": lambda: ""},
}


class Command(BaseCommand):
    help = "Generate fake data"

    def add_arguments(self, parser):
        parser.add_argument("--from-file")
        parser.add_argument("--to-file")
        parser.add_argument("--quantity", type=int, default=100_000)
        parser.add_argument("type", choices=["object", "relationship", "dataset"])
        parser.add_argument(
            "name", choices=["Person", "Company", "Candidacy", "runs_for", "is_partner", "represents", "bemdeclarado"]
        )
        parser.add_argument("output_filename")

    def handle(self, *args, **kwargs):
        from_file = kwargs["from_file"]
        to_file = kwargs["to_file"]
        type_ = kwargs["type"]
        name = kwargs["name"]
        quantity = kwargs["quantity"]
        output_filename = kwargs["output_filename"]
        if type_ == "object":
            create_func = {
                "Person": create_person,
                "Company": create_company,
                "Candidacy": create_candidacy,
            }[name]
            writer = rows.utils.CsvLazyDictWriter(output_filename)
            for _ in tqdm(range(quantity)):
                writer.writerow(create_func())
            writer.close()

        elif type_ == "relationship":
            fields = {"is_partner": is_partner_fields, "runs_for": runs_for_fields, "represents": represents_fields}[
                name
            ]
            if not from_file or not to_file:
                raise ValueError("For relationship must specify --from-file and --to-file")
            with rows.utils.open_compressed(from_file) as fobj:
                from_uuids = [row["object_uuid"] for row in tqdm(csv.DictReader(fobj), desc="Reading from_file")]
            with rows.utils.open_compressed(to_file) as fobj:
                to_uuids = [row["object_uuid"] for row in tqdm(csv.DictReader(fobj), desc="Reading to_file")]

            writer = rows.utils.CsvLazyDictWriter(output_filename)
            progress = tqdm(desc="Generating relationships")
            count = 0
            while count < quantity:
                for from_uuid in from_uuids:
                    if random.randint(0, 100) > 10:
                        continue
                    if random.randint(0, 100) > 5:
                        relationships = random.randint(1, 5)
                    else:
                        relationships = random.randint(5, 50)
                    for _ in range(relationships):
                        to_uuid = random.choice(to_uuids)
                        # TODO: what if it choose the same to_uuid?
                        writer.writerow(
                            {
                                "from_node_uuid": from_uuid,
                                "to_node_uuid": to_uuid,
                                "properties": json.dumps(
                                    {key: str(value or "") for key, value in generate_row(fields).items()}
                                ),
                            }
                        )
                        count += 1
                        progress.update()
                        if count == quantity:
                            break
                    if count == quantity:
                        break
            progress.close()
            writer.close()

        elif type_ == "dataset":
            fields = {"bemdeclarado": bemdeclarado_fields}[name]
            if not from_file:
                raise ValueError("For dataset must specify --from-file")
            with rows.utils.open_compressed(from_file) as fobj:
                from_uuids = [row["object_uuid"] for row in tqdm(csv.DictReader(fobj), desc="Reading from_file")]

            writer = rows.utils.CsvLazyDictWriter(output_filename)
            progress = tqdm(desc="Generating data")
            count = 0
            while count < quantity:
                for from_uuid in from_uuids:
                    if random.randint(0, 100) > 10:
                        continue
                    data_rows = random.randint(0, 50)
                    for _ in range(data_rows):
                        writer.writerow(
                            {
                                "object_uuid": from_uuid,
                                **{key: str(value or "") for key, value in generate_row(fields).items()},
                            }
                        )
                        count += 1
                        progress.update()
                        if count == quantity:
                            break
                    if count == quantity:
                        break
            progress.close()
            writer.close()
