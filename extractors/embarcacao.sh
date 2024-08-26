#!/bin/bash

set -e
mkdir -p data/download data/output

DATASET="embarcacao"
URL="https://www.marinha.mil.br/tm/sites/www.marinha.mil.br.tm/files/file/registro/documentos/reb.xlsx"
DOWNLOAD_FILENAME="data/download/${DATASET}_orig.xlsx"
FIXED_FILENAME="data/download/${DATASET}-fixed_orig.csv.gz"
TABLE_NAME="${DATASET}_orig"
SCHEMA_FILENAME="schema/${DATASET}_orig.csv"
ENCODING="utf-8"
DIALECT="excel"
SQL_FILENAME="sql/dataset_${DATASET}.sql"
OUTPUT_FILENAME="data/output/dataset_${DATASET}.csv.gz"


# Baixa e corrige arquivo
wget --user-agent="Mozilla/5.0" -O "$DOWNLOAD_FILENAME" "$URL"
python embarcacao.py "$DOWNLOAD_FILENAME" "$FIXED_FILENAME"

# Importa CSV no banco de dados
echo "DROP TABLE IF EXISTS $TABLE_NAME CASCADE" | psql "$DATABASE_URL"
rows pgimport \
      --input-encoding="$ENCODING" \
      --dialect="$DIALECT" \
      --schema=$SCHEMA_FILENAME \
      "$FIXED_FILENAME" \
      "$DATABASE_URL" \
      "$TABLE_NAME"

# Exporta resultado da consulta para arquivo que será importado no sistema
rows pgexport --is-query "$DATABASE_URL" "$(cat $SQL_FILENAME)" "$OUTPUT_FILENAME"
