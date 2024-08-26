import re
import uuid
from json import dumps as json_dump
from pathlib import Path

import psycopg2
from rows.utils import CsvLazyDictWriter
from tqdm import tqdm

REGEXP_POSTGRESQL_URI = re.compile("^postgres://([^:]+):([^@]+)@([^:]+):([^/]+)/(.*)$")


def export_csv(iterator, filename):
    writer = CsvLazyDictWriter(filename)
    for row in tqdm(iterator, desc=filename.name):
        writer.writerow({key: value if not isinstance(value, dict) else json_dump(value) for key, value in row.items()})


class DatabaseExtractor:
    def __init__(self, database_url):
        user, password, host, port, dbname = REGEXP_POSTGRESQL_URI.findall(database_url)[0]
        self.connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            dbname=dbname,
        )

    def execute(self, sql, batch_size=100_000):
        cursor = self.connection.cursor(uuid.uuid4().hex)
        cursor.execute(sql)
        finished, header = False, None
        while not finished:
            data = cursor.fetchmany(batch_size)
            if header is None:
                header = [item[0] for item in cursor.description]
            for row in data:
                yield dict(zip(header, row))
            finished = len(data) != batch_size
        cursor.close()

    def tables(self):
        sql = (
            "SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"
        )
        yield from self.execute(sql)

    def row_count(self, schema, table):
        sql = f"SELECT n_live_tup FROM pg_stat_user_tables WHERE schemaname = '{schema}' AND relname = '{table}'"
        return list(self.execute(sql))[0]["n_live_tup"]

    def table_columns(self, schema, table):
        sql = f"SELECT * FROM information_schema.columns WHERE table_schema = '{schema}' AND table_name = '{table}'"
        yield from self.execute(sql)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=250_000)
    parser.add_argument("--skip-tables")
    parser.add_argument("database_url")
    parser.add_argument("output_path")
    args = parser.parse_args()

    output_path = Path(args.output_path)
    if not output_path.exists():
        output_path.mkdir(parents=True)
    skip_tables = args.skip_tables
    if skip_tables:
        skip_tables = [item.strip() for item in skip_tables.split(",") if item.strip()]

    db = DatabaseExtractor(args.database_url)

    # Get table information
    tables = list(db.tables())

    # Export all columns for each table found
    columns = []
    for table in tables:
        schema, table_name = table["schemaname"], table["tablename"]
        if skip_tables and table_name in skip_tables:
            continue
        for row in db.table_columns(table["schemaname"], table["tablename"]):
            columns.append(row)
    export_csv(columns, output_path / "columns.csv.gz")

    # Export estimate row count for each table found
    row_count = []
    for table in tables:
        schema, table_name = table["schemaname"], table["tablename"]
        if skip_tables and table_name in skip_tables:
            continue
        row_count.append(
            {
                "schemaname": table["schemaname"],
                "tablename": table["tablename"],
                "count": db.row_count(table["schemaname"], table["tablename"]),
            }
        )
    export_csv(row_count, output_path / "rowcount.csv.gz")

    # Export a sample for each table found
    for table in tables:
        schema, table_name = table["schemaname"], table["tablename"]
        if skip_tables and table_name in skip_tables:
            continue
        sql = f'SELECT * FROM "{schema}"."{table_name}" LIMIT {args.sample}'
        export_csv(db.execute(sql), output_path / f"sample-{schema}-{table_name}.csv.gz")


if __name__ == "__main__":
    main()
