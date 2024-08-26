import csv
from pathlib import Path

MAPPING_PATH = Path(__file__).parent / "mapping"


def load_mapping(filename, convert_int=True):
    with (MAPPING_PATH / filename).open() as fobj:
        if convert_int:
            return [(int(row["codigo"]), row["descricao"]) for row in csv.DictReader(fobj)]
        else:
            return [(row["codigo"], row["descricao"]) for row in csv.DictReader(fobj)]


MUNICIPIO = load_mapping("municipio.csv", convert_int=True)
PAIS = load_mapping("pais.csv", convert_int=True)

PESSOA_FISICA_NATUREZA_OCUPACAO = load_mapping("pessoa-fisica-natureza-ocupacao.csv", convert_int=True)
PESSOA_FISICA_OCUPACAO_PRINCIPAL = load_mapping("pessoa-fisica-ocupacao-principal.csv", convert_int=True)
PESSOA_FISICA_SITUACAO_CADASTRAL = load_mapping("pessoa-fisica-situacao-cadastral.csv", convert_int=True)

EMPRESA_CNAE = load_mapping("empresa-cnae.csv", convert_int=False)
EMPRESA_MOTIVO_SITUACAO_CADASTRAL = load_mapping("empresa-motivo-situacao-cadastral.csv", convert_int=True)
EMPRESA_NATUREZA_JURIDICA = load_mapping("empresa-natureza-juridica.csv", convert_int=True)
EMPRESA_PORTE = load_mapping("empresa-porte.csv", convert_int=True)
EMPRESA_QUALIFICACAO_SOCIO = load_mapping("empresa-qualificacao-socio.csv", convert_int=True)
EMPRESA_SITUACAO_CADASTRAL = load_mapping("empresa-situacao-cadastral.csv", convert_int=True)

BEM_DECLARADO_TIPO = load_mapping("bem-declarado-tipo.csv", convert_int=True)
