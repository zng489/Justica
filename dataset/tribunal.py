import re

import requests
from lxml.html import document_fromstring

REGEXP_TRE = re.compile("tre-([a-z]{2}).jus.br")
REGEXP_TRIBUNAL = re.compile(r"(.*) \((.*)\)")


def tribunais():
    url = "https://www.cnj.jus.br/poder-judiciario/tribunais/"
    response = requests.get(url)
    tree = document_fromstring(response.text)
    items = tree.xpath("//a[contains(@href, '/tribunais/') or contains(@href, 'tre-')]")
    for item in items:
        text, link = item.xpath("./text()")[0], item.xpath("./@href")[0]
        if text in ("Sites dos Tribunais", "acesse apenas a lista"):
            continue
        result = REGEXP_TRIBUNAL.findall(text)
        if result:
            text, acronym = result[0]
        else:
            acronym = None
        if text.startswith("Tribunal Regional Eleitoral"):
            acronym = "TRE" + REGEXP_TRE.findall(link)[0].upper()
        yield {
            "sigla": acronym,
            "nome": text,
            "link": link,
        }


if __name__ == "__main__":
    import argparse
    import csv

    parser = argparse.ArgumentParser()
    parser.add_argument("csv_filename")
    args = parser.parse_args()

    with open(args.csv_filename, mode="w") as fobj:
        writer = csv.DictWriter(fobj, fieldnames=["sigla", "nome", "link"])
        writer.writeheader()
        for tribunal in tribunais():
            writer.writerow(tribunal)
