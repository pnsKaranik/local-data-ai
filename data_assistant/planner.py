from data_assistant.domain.plan import QueryPlan
from data_assistant.llm.ollama import OllamaClient
from data_assistant.schema_linker import SchemaMatch


class QueryPlanner:
    def __init__(
        self,
        llm: OllamaClient,
    ) -> None:
        self.llm = llm

    def create_plan(
        self,
        question: str,
        schema_matches: list[SchemaMatch],
    ) -> QueryPlan:
        prompt = self._build_prompt(
            question=question,
            schema_matches=schema_matches,
        )

        return self.llm.generate_structured(
            prompt=prompt,
            response_model=QueryPlan,
        )

    def _build_prompt(
        self,
        question: str,
        schema_matches: list[SchemaMatch],
    ) -> str:
        schema_lines = []

        for match in schema_matches:
            schema_lines.append(
                f"Table: {match.table.name}"
            )

            for column_match in match.columns:
                column = column_match.column

                schema_lines.append(
                    f"- Column: {column.name}, "
                    f"type: {column.dtype}, "
                    f"description: {column.description}"
                )

        schema_context = "\n".join(schema_lines)

        return f"""
You are a query planner.

Convert the user's question into a structured QueryPlan.

Use ONLY tables and columns provided in the schema.

Do NOT generate SQL.
Do NOT invent tables.
Do NOT invent columns.

Schema:

{schema_context}

User question:

{question}
""".strip()