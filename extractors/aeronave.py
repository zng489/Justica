import argparse

import rows
from rows.fields import make_header, slug


def extract_values(line, separators):
    column_length = [len(part) for part in separators.split()]
    values = []
    start = 0
    for length in column_length:
        if line[start + length] != " ":  # Field separator
            raise ValueError(f"Malformed row: {line}")
        value = line[start : start + length].strip()
        values.append(value)
        start += length + 1  # 1 for space
    return values


def extract_header(header_line, separators):
    return make_header(
        [slug(field_name.lower().replace("<br>", " ")) for field_name in extract_values(header_line, separators)]
    )


def extract_rows(txt_filename, input_encoding):
    with open(txt_filename, encoding=input_encoding) as fobj:
        fobj.readline()  # Discard first line, "Relatório RRAB"
        header_line = fobj.readline()
        separators = fobj.readline()
        header = extract_header(header_line, separators)

        replace_map = {
            "operador": "nm_operador",
            "cpf_cnpj_2": "cpf_cgc",
            "cod": "cod_fabricante",
            "nome_fabricante": "nm_fabricante",
            "nome_fab_rab": "nm_fabricante_rab",
            "ano": "nr_ano_fabricacao",
            "modelo": "ds_modelo",
            "modelo_rab": "ds_modelo_rab",
            "ass": "nr_assentos",
            "tr": "nr_tripulacao_min",
            "pax": "nr_passageiros_max",
            "num_serie": "nr_serie",
            "matricul": "nr_cert_matricula",
            "motivo": "ds_motivo_canc",
            "data_can": "dt_canc",
            "descricao_do_gravame": "ds_gravame",
            "moe": "moeda",
            "f": "proprietario_tipo_pessoa",
            "f_2": "operador_tipo_pessoa",
        }
        header = [replace_map.get(item, item) for item in header]
        for line in fobj:
            try:
                values = extract_values(line, separators)
            except ValueError:  # Malformed row, skip
                continue
            yield dict(zip(header, values))


def export_csv(data, csv_filename, output_encoding):
    writer = rows.utils.CsvLazyDictWriter(csv_filename, encoding=output_encoding)
    for row in data:
        writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-encoding", default="iso-8859-15")
    parser.add_argument("--output-encoding", default="utf-8")
    parser.add_argument("txt_filename")
    parser.add_argument("csv_filename")
    args = parser.parse_args()

    data = extract_rows(args.txt_filename, args.input_encoding)
    export_csv(data, args.csv_filename, args.output_encoding)
