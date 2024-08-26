#!/bin/bash

set -e
mkdir -p data/download data/output

DATASET="aeronave"
INPUT_FILENAME="data/download/Relatorio.TXT"
FIXED_FILENAME="data/download/${DATASET}_orig.csv"
SCHEMA_FILENAME="schema/${DATASET}_orig.csv"
OUTPUT_FILENAME="data/output/dataset_${DATASET}.csv.gz"
ORIG_TABLE_NAME="${DATASET}_orig"
OUTPUT_VIEW="dataset_${DATASET}"
SQL_FILENAME="sql/dataset_${DATASET}.sql"


# Converte arquivo TXT (original, já baixado) para CSV, normalizando nomes de colunas
python aeronave.py "$INPUT_FILENAME" "$FIXED_FILENAME"

# Importa CSV no banco de dados
echo "DROP TABLE IF EXISTS $TABLE_NAME CASCADE" | psql "$DATABASE_URL"
rows pgimport \
	--input-encoding="utf-8" \
	--dialect="excel" \
	--schema="$SCHEMA_FILENAME" \
	"$FIXED_FILENAME" "$DATABASE_URL" "$ORIG_TABLE_NAME"

# Cria view com transformações
cat "$SQL_FILENAME" | psql "$DATABASE_URL"

# Exporta resultado da view para importação no sistema
rows pgexport --is-query "$DATABASE_URL" "SELECT * FROM $OUTPUT_VIEW" "$OUTPUT_FILENAME"
