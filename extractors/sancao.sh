#!/bin/bash

set -e
mkdir -p data/download data/output

DATASET="sancao"
URL1="https://transparencia.gov.br/download-de-dados/ceis/20220822"
DOWNLOAD_FILENAME1="data/download/${DATASET}_inidonea_orig.zip"
URL2="https://transparencia.gov.br/download-de-dados/cepim/20220819"
DOWNLOAD_FILENAME2="data/download/${DATASET}_impedida_orig.zip"
URL3="https://transparencia.gov.br/download-de-dados/cnep/20220822"
DOWNLOAD_FILENAME3="data/download/${DATASET}_punida_orig.zip"
URL4="https://transparencia.gov.br/download-de-dados/acordos-leniencia/20220822"
DOWNLOAD_FILENAME4="data/download/${DATASET}_leniencia_orig.zip"
NORMALIZED_FILENAME="data/download/${DATASET}_normalizado_orig.csv.gz"
TABLE_NAME="${DATASET}_orig"
SCHEMA_FILENAME="schema/${DATASET}_normalizado_orig.csv"
ENCODING="utf-8"
DIALECT="excel"
SQL_FILENAME="sql/dataset_${DATASET}.sql"
OUTPUT_FILENAME="data/output/dataset_${DATASET}.csv.xz"


# Baixa e normaliza arquivos
wget -O "$DOWNLOAD_FILENAME1" "$URL1"
wget -O "$DOWNLOAD_FILENAME2" "$URL2"
wget -O "$DOWNLOAD_FILENAME3" "$URL3"
wget -O "$DOWNLOAD_FILENAME4" "$URL4"
python sancao.py \
	"$DOWNLOAD_FILENAME1" \
	"$DOWNLOAD_FILENAME2" \
	"$DOWNLOAD_FILENAME3" \
	"$DOWNLOAD_FILENAME4" \
	"$NORMALIZED_FILENAME"

# Importa CSV no banco de dados
echo "DROP TABLE IF EXISTS $TABLE_NAME CASCADE" | psql "$DATABASE_URL"
rows pgimport \
      --input-encoding="$ENCODING" \
      --dialect="$DIALECT" \
      --schema=$SCHEMA_FILENAME \
      "$NORMALIZED_FILENAME" \
      "$DATABASE_URL" \
      "$TABLE_NAME"

# Exporta resultado da consulta para arquivo que será importado no sistema
rows pgexport --is-query "$DATABASE_URL" "$(cat $SQL_FILENAME)" "$OUTPUT_FILENAME"
