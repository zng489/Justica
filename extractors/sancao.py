import csv
import datetime
import io
from pathlib import Path
from unicodedata import normalize
from zipfile import ZipFile

import rows
from rows.fields import slug


def unaccent(value):
    return normalize("NFKD", value).encode("ascii", errors="ignore").decode("ascii")


class PtBrDateField(rows.fields.DateField):
    @classmethod
    def deserialize(cls, value):
        value = str(value or "").strip()
        if not value:
            return None
        return datetime.datetime.strptime(value, "%d/%m/%Y").date()


class PtBrMoneyField(rows.fields.DecimalField):
    @classmethod
    def deserialize(cls, value):
        value = str(value or "").strip()
        if not value:
            return None
        return super().deserialize(value.replace(",", "."))


def get_zipped_csv_rows(zip_filename, csv_pattern):
    zf = ZipFile(zip_filename)

    for fileinfo in zf.filelist:
        if csv_pattern in fileinfo.filename:
            fobj = zf.open(fileinfo.filename)
            break
    reader = csv.DictReader(
        io.TextIOWrapper(fobj, encoding="iso-8859-15"),
        delimiter=";",
    )
    for row in reader:
        yield {slug(key): value for key, value in row.items()}


def normalize_file(zip_filename):
    file_type = Path(zip_filename).name.replace("sancao_", "").split("_")[0]

    if file_type == "inidonea":
        for row in get_zipped_csv_rows(filename, "CEIS.csv"):
            if row["tipo_de_pessoa"] == "J":
                nome = row["razao_social_cadastro_receita"]
            else:
                nome = row["nome_informado_pelo_orgao_sancionador"]
            nome = unaccent(nome).upper().strip()
            yield {
                "nome": nome,
                "documento": row["cpf_ou_cnpj_do_sancionado"],
                "processo": row["numero_do_processo"],
                "tipo": f"Inidônea/Suspensa - {row['tipo_sancao']}",
                "data_inicio": PtBrDateField.deserialize(row["data_inicio_sancao"]),
                "data_final": PtBrDateField.deserialize(row["data_final_sancao"]),
                "orgao": row["orgao_sancionador"],
                "fundamentacao": row["fundamentacao_legal"],
                "multa": None,
            }

    elif file_type == "impedida":
        for row in get_zipped_csv_rows(filename, "CEPIM.csv"):
            nome = unaccent(row["nome_entidade"]).upper().strip()
            yield {
                "nome": nome,
                "documento": row["cnpj_entidade"],
                "processo": row["numero_convenio"],
                "tipo": "Impedida de licitar",
                "data_inicio": None,
                "data_final": None,
                "orgao": row["orgao_concedente"],
                "fundamentacao": row["motivo_do_impedimento"],
                "multa": None,
            }

    elif file_type == "punida":
        for row in get_zipped_csv_rows(filename, "CNEP.csv"):
            if row["tipo_de_pessoa"] == "J":
                nome = row["razao_social_cadastro_receita"]
            else:
                nome = row["nome_informado_pelo_orgao_sancionador"]
            nome = unaccent(nome).upper().strip()
            yield {
                "nome": nome,
                "documento": row["cpf_ou_cnpj_do_sancionado"],
                "processo": row["numero_do_processo"],
                "tipo": f"Punida - {row['tipo_sancao']}",
                "data_inicio": PtBrDateField.deserialize(row["data_inicio_sancao"]),
                "data_final": PtBrDateField.deserialize(row["data_final_sancao"]),
                "orgao": row["orgao_sancionador"],
                "fundamentacao": row["fundamentacao_legal"],
                "multa": PtBrMoneyField.deserialize(row["valor_da_multa"]),
            }

    elif file_type == "leniencia":
        for row in get_zipped_csv_rows(filename, "Acordos.csv"):
            if not row["cnpj_do_sancionado"].isdigit():  # Empresas exteriores
                continue
            nome = unaccent(row["razao_social_cadastro_receita"]).upper().strip()
            yield {
                "nome": nome,
                "documento": row["cnpj_do_sancionado"],
                "processo": row["numero_do_processo"],
                "tipo": f"Acordo de leniência ({row['situacao_do_acordo_de_lenienica']})",
                "data_inicio": PtBrDateField.deserialize(row["data_de_inicio_do_acordo"]),
                "data_final": PtBrDateField.deserialize(row["data_de_fim_do_acordo"]),
                "orgao": row["orgao_sancionador"],
                "fundamentacao": None,
                "multa": None,
            }


if __name__ == "__main__":
    import argparse

    from tqdm import tqdm

    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", nargs="+")
    parser.add_argument("csv_filename")
    args = parser.parse_args()

    writer = rows.utils.CsvLazyDictWriter(args.csv_filename)
    for filename in tqdm(args.input_filename):
        for row in normalize_file(filename):
            writer.writerow(row)
    writer.close()
