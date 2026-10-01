from pathlib import Path

from data_assistant.data.catalog import Catalog

import yaml

SEMANTIC_FILE = Path(__file__).with_name("semantic.yaml")

def load_semantic_metadata() -> dict:
    with SEMANTIC_FILE.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data or {}

def apply_semantic_metadata(
    catalog: Catalog,
    metadata: dict,
) -> Catalog:

    tables_metadata = metadata.get("tables", {})

    for table in catalog.tables:
        table_metadata = tables_metadata.get(table.name, {})

        table.description = table_metadata.get(
            "description",
            table.description,
        )

        table.synonyms = table_metadata.get(
            "synonyms",
            table.synonyms,
        )

        columns_metadata = table_metadata.get("columns", {})

        for column in table.columns:
            column_metadata = columns_metadata.get(column.name, {})

            column.description = column_metadata.get(
                "description",
                column.description,
            )

            column.synonyms = column_metadata.get(
                "synonyms",
                column.synonyms,
            )

            column.unit = column_metadata.get(
                "unit",
                column.unit,
            )

    return catalog