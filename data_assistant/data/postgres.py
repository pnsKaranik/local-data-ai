import psycopg
from psycopg import Connection, sql

from data_assistant.config import get_settings
from data_assistant.data.catalog import Catalog, Column, DType, Table


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


def get_columns(
    table_name: str,
) -> list[tuple[str, str]]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                ORDER BY ordinal_position
                """,
                (table_name,),
            )

            rows = cursor.fetchall()

    return rows


def map_postgres_type(
    data_type: str,
) -> DType:
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


def get_column_samples(
    table_name: str,
    column_name: str,
    limit: int = 5,
) -> list[str]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            query = sql.SQL(
                """
                SELECT DISTINCT {column}
                FROM {table}
                WHERE {column} IS NOT NULL
                LIMIT %s
                """
            ).format(
                column=sql.Identifier(column_name),
                table=sql.Identifier(table_name),
            )

            cursor.execute(
                query,
                (limit,),
            )

            rows = cursor.fetchall()

    return [
        str(row[0])
        for row in rows
    ]


def get_column_stats(
    table_name: str,
    column_name: str,
) -> dict:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            query = sql.SQL(
                """
                SELECT
                    COUNT(DISTINCT {column}),
                    COUNT(*) FILTER (
                        WHERE {column} IS NULL
                    ),
                    MIN({column}),
                    MAX({column}),
                    COUNT({column})
                FROM {table}
                """
            ).format(
                column=sql.Identifier(column_name),
                table=sql.Identifier(table_name),
            )

            cursor.execute(query)

            row = cursor.fetchone()

    if row is None:
        return {
            "distinct": 0,
            "nulls": 0,
            "min": None,
            "max": None,
            "unique": False,
        }

    distinct_count = row[0]
    null_count = row[1]
    min_value = row[2]
    max_value = row[3]
    non_null_count = row[4]

    return {
        "distinct": distinct_count,
        "nulls": null_count,
        "min": (
            str(min_value)
            if min_value is not None
            else None
        ),
        "max": (
            str(max_value)
            if max_value is not None
            else None
        ),
        "unique": (
            non_null_count > 0
            and distinct_count == non_null_count
        ),
    }


def load_table(
    table_name: str,
) -> Table:
    column_rows = get_columns(table_name)

    columns = []

    for column_name, data_type in column_rows:
        dtype = map_postgres_type(data_type)

        samples = get_column_samples(
            table_name=table_name,
            column_name=column_name,
        )

        stats = get_column_stats(
            table_name=table_name,
            column_name=column_name,
        )

        column = Column(
            name=column_name,
            dtype=dtype,
            samples=samples,
            distinct=stats["distinct"],
            nulls=stats["nulls"],
            min=stats["min"],
            max=stats["max"],
            unique=stats["unique"],
        )

        columns.append(column)

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