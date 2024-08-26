#!/bin/bash

set -e
mkdir -p data/download data/output

DATASET="bem_declarado"
URL="https://data.brasil.io/dataset/eleicoes-brasil/bem-declarado.csv.gz"
DOWNLOAD_FILENAME="data/download/${DATASET}_orig.csv.gz"
TABLE_NAME="${DATASET}_orig"
SCHEMA_FILENAME="schema/${DATASET}_orig.csv"
ENCODING="utf-8"
DIALECT="excel"
SQL_FILENAME="sql/dataset_${DATASET}.sql"
OUTPUT_VIEW="dataset_${DATASET}"
OUTPUT_FILENAME="data/output/dataset_${DATASET}.csv.gz"


# Baixa arquivo (já convertido pelo Brasil.IO)
wget -O "$DOWNLOAD_FILENAME" "$URL"

# Importa CSV no banco de dados
echo "DROP TABLE IF EXISTS $TABLE_NAME CASCADE" | psql "$DATABASE_URL"
rows pgimport \
      --input-encoding="$ENCODING" \
      --dialect="$DIALECT" \
      --schema=$SCHEMA_FILENAME \
      "$DOWNLOAD_FILENAME" \
      "$DATABASE_URL" \
      "$TABLE_NAME"

# Cria view com transformações
cat "$SQL_FILENAME" | psql "$DATABASE_URL"

# Exporta resultado da view para importação no sistema
rows pgexport --is-query "$DATABASE_URL" "SELECT * FROM $OUTPUT_VIEW" "$OUTPUT_FILENAME"
