"""
Get sample from fake data (imported on database) so we can have fakeapi
returning existing person/companies.
"""

import csv
import random

import rows
from tqdm import tqdm


def extract_data(input_filename, field_names, output_filename):
    fobj = rows.utils.open_compressed(input_filename)
    data = [{field: row[field] for field in field_names} for row in tqdm(csv.DictReader(fobj))]
    random.shuffle(data)
    writer = rows.utils.CsvLazyDictWriter(output_filename)
    for _ in tqdm(range(1_000)):
        row = data.pop()
        writer.writerow(row)
    writer.close()


input_filename = "../data/fake/fake-object-person.csv.xz"
output_filename = "./source/person.csv.gz"
field_names = ["cpf", "nome"]
extract_data(input_filename, field_names, output_filename)

input_filename = "../data/fake/fake-object-company.csv.xz"
output_filename = "./source/company.csv.gz"
field_names = ["cnpj", "razao_social"]
extract_data(input_filename, field_names, output_filename)
