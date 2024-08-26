#!/bin/bash

set -e
mkdir -p data/download data/output

URL="https://sistemas.anac.gov.br/dadosabertos/Aeronaves/RAB/dados_aeronaves.csv"
DOWNLOAD_FILENAME="data/download/aeronave_dadosabertos_orig-error.csv"
FIXED_FILENAME="data/download/aeronave_dadosabertos_orig-fixed.csv.gz"
TABLE_NAME="aeronave_dadosabertos_orig"
SCHEMA_FILENAME="schema/aeronave_dadosabertos_orig.csv"
ENCODING="UTF-8"
DIALECT="excel-semicolon"
SQL_FILENAME="sql/dataset_aeronave_dadosabertos.sql"
OUTPUT_VIEW="dataset_aeronave_dadosabertos"
OUTPUT_FILENAME="data/output/dataset_aeronave_dadosabertos.csv.gz"

# Baixa e corrige arquivo da fonte oficial
wget -O "$DOWNLOAD_FILENAME" "$URL"
egrep -v 'Atualizado em:' "$DOWNLOAD_FILENAME" | sed 's/"null"/""/g' | gzip - > "$FIXED_FILENAME"
rm "$DOWNLOAD_FILENAME"

# Importa CSV no banco de dados
echo "DROP TABLE IF EXISTS $TABLE_NAME CASCADE" | psql "$DATABASE_URL"
rows pgimport \
      --input-encoding="$ENCODING" \
      --dialect="$DIALECT" \
      --schema=$SCHEMA_FILENAME \
      "$FIXED_FILENAME" \
      "$DATABASE_URL" \
      "$TABLE_NAME"

# Cria view com transformações
cat "$SQL_FILENAME" | psql "$DATABASE_URL"

# Exporta resultado da view para importação no sistema
rows pgexport --is-query "$DATABASE_URL" "SELECT * FROM $OUTPUT_VIEW" "$OUTPUT_FILENAME"
