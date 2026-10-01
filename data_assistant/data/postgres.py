import psycopg
from psycopg import Connection

from data_assistant.data.catalog import DType, Column, Table, Catalog
from data_assistant.config import get_settings

def get_connection() -> Connection:
    settings = get_settings()

    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_database,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )

def get_table_names() -> list[str]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            )

            rows = cursor.fetchall()

    return [row[0] for row in rows]

def get_columns(table_name: str) -> list[tuple[str, str]]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                    AND table_name = %s
                ORDER BY ordinal_positon
                """,
                (table_name,),
            )

            rows = cursor.fetchall()
    return rows

def map_postgres_type(data_type: str) -> DType:
    if data_type in {
        "smallint",
        "integer",
        "bigint",
        "numeric",
        "decimal",
        "real",
        "double precision",
    }:
        return "number"

    if data_type in {
        "date",
        "timestamp without time zone",
        "timestamp with time zone",
        "time without time zone",
        "time with time zone",
    }:
        return "date"

    if data_type == "boolean":
        return "bool"

    return "text"

def load_table(table_name: str) -> Table:
    column_rows = get_columns(table_name)

    columns = [
        Column(
            name=column_name,
            dtype=map_postgres_type(data_type)
        )
        for column_name, data_type in column_rows
    ]

    return Table(
        name=table_name,
        columns=columns,
    )

def load_catalog() -> Catalog:
    table_names = get_table_names()

    tables = [
        load_table(table_name)
        for table_name in table_names
    ]

    return Catalog(
        tables=tables,
    )