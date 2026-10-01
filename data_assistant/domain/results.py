from typing import Any
from pydantic import Field
from data_assistant.domain.plan import StrictModel

class QueryResult(StrictModel):
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0