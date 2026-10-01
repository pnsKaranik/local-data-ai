from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

DType = Literal[
    "text",
    "number",
    "date",
    "bool",
]

@dataclass
class Column:
    name: str
    dtype: DType = "text"
    description: str = ""
    unit: str | None = None
    synonyms: list[str] = field(default_factory=list)
    samples: list[str] = field(default_factory=list)
    distinct: int | None = None
    nulls: int = 0
    min: str | None = None
    max: str | None = None
    unique: bool = False

@dataclass
class Table:
    name: str
    description: str = ""
    synonyms: list[str] = field(default_factory=list)
    columns: list[Column] = field(default_factory=list)

    def get_column(self, name: str) -> Column | None:
        for column in self.columns:
            if column.name == name:
                return column

        return None

@dataclass
class Catalog:
    tables: list[Table] = field(default_factory=list)

    def get_table(self, name: str) -> Table | None:
        for table in self.tables:
            if table.name == name:
                return table

        return None