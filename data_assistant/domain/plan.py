from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True
    )

class Filter(StrictModel):
    column: str
    operator: Literal[
        "=",
        "!=",
        ">",
        ">=",
        "<",
        "<=",
        "in",
        "not_in",
        "contains",
    ]
    value: str | int | float | bool | list[str] | list[int] | list[float]

class Dimension(StrictModel):
    column: str

class Measure(StrictModel):
    column: str
    aggregation: Literal[
        "sum",
        "avg",
        "count",
        "min",
        "max",
    ]

class Sort(StrictModel):
    column: str
    direction: Literal[
        "asc",
        "desc",
    ] = "asc"

class QueryPlan(StrictModel):
    kind: Literal["rows", "aggregated"]
    table: str
    filters: list[Filter] = Field(default_factory=list)
    dimensions: list[Dimension] = Field(default_factory=list)
    measures: list[Measure] = Field(default_factory=list)
    order_by: list[Sort] = Field(default_factory=list)

    limit: int = 100