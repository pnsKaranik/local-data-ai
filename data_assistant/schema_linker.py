import re
from dataclasses import dataclass, field

from rapidfuzz import fuzz

from data_assistant.data.catalog import Catalog, Column, Table


FUZZY_THRESHOLD = 0.85


@dataclass
class ColumnMatch:
    column: Column
    score: float


@dataclass
class TableMatch:
    table: Table
    score: float


@dataclass
class SchemaMatch:
    table: Table
    table_score: float
    columns: list[ColumnMatch] = field(default_factory=list)


def normalize_text(text: str) -> str:
    text = text.lower()

    text = re.sub(
        r"[^a-z0-9_ ]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def fuzzy_similarity(
    text_a: str,
    text_b: str,
) -> float:
    normalized_a = normalize_text(text_a)
    normalized_b = normalize_text(text_b)

    if not normalized_a or not normalized_b:
        return 0.0

    score = fuzz.ratio(
        normalized_a,
        normalized_b,
    )

    return score / 100.0


def score_name(
    question: str,
    name: str,
    synonyms: list[str],
) -> float:
    normalized_question = normalize_text(question)
    normalized_name = normalize_text(name)

    if normalized_name and normalized_name in normalized_question:
        return 1.0

    for synonym in synonyms:
        normalized_synonym = normalize_text(synonym)

        if (
            normalized_synonym
            and normalized_synonym in normalized_question
        ):
            return 1.0

    candidates = [
        name,
        *synonyms,
    ]

    best_score = 0.0

    for candidate in candidates:
        normalized_candidate = normalize_text(candidate)

        if not normalized_candidate:
            continue

        for word in normalized_question.split():
            score = fuzzy_similarity(
                normalized_candidate,
                word,
            )

            best_score = max(
                best_score,
                score,
            )

    if best_score >= FUZZY_THRESHOLD:
        return best_score

    return 0.0


def score_description(
    question: str,
    description: str,
) -> float:
    if not description:
        return 0.0

    normalized_question = normalize_text(question)
    normalized_description = normalize_text(description)

    score = fuzz.token_set_ratio(
        normalized_question,
        normalized_description,
    )

    score = score / 100.0

    if score >= FUZZY_THRESHOLD:
        return score

    return 0.0


def score_samples(
    question: str,
    column: Column,
) -> float:
    normalized_question = normalize_text(question)

    for sample in column.samples:
        normalized_sample = normalize_text(
            str(sample)
        )

        if (
            normalized_sample
            and normalized_sample in normalized_question
        ):
            return 1.0

    return 0.0


def score_column(
    question: str,
    column: Column,
) -> float:
    name_score = score_name(
        question=question,
        name=column.name,
        synonyms=column.synonyms,
    )

    description_score = score_description(
        question=question,
        description=column.description,
    )

    sample_score = score_samples(
        question=question,
        column=column,
    )

    return max(
        name_score,
        description_score,
        sample_score,
    )


def score_table(
    question: str,
    table: Table,
) -> float:
    name_score = score_name(
        question=question,
        name=table.name,
        synonyms=table.synonyms,
    )

    description_score = score_description(
        question=question,
        description=table.description,
    )

    column_score = 0.0

    for column in table.columns:
        score = score_column(
            question=question,
            column=column,
        )

        column_score = max(
            column_score,
            score,
        )

    return max(
        name_score,
        description_score,
        column_score,
    )


def rank_columns(
    question: str,
    table: Table,
    min_score: float = FUZZY_THRESHOLD,
) -> list[ColumnMatch]:
    matches = []

    for column in table.columns:
        score = score_column(
            question=question,
            column=column,
        )

        if score >= min_score:
            matches.append(
                ColumnMatch(
                    column=column,
                    score=score,
                )
            )

    matches.sort(
        key=lambda match: match.score,
        reverse=True,
    )

    return matches


def rank_tables(
    question: str,
    catalog: Catalog,
    min_score: float = FUZZY_THRESHOLD,
) -> list[TableMatch]:
    matches = []

    for table in catalog.tables:
        score = score_table(
            question=question,
            table=table,
        )

        if score >= min_score:
            matches.append(
                TableMatch(
                    table=table,
                    score=score,
                )
            )

    matches.sort(
        key=lambda match: match.score,
        reverse=True,
    )

    return matches


def link_schema(
    question: str,
    catalog: Catalog,
) -> list[SchemaMatch]:
    table_matches = rank_tables(
        question=question,
        catalog=catalog,
    )

    schema_matches = []

    for table_match in table_matches:
        column_matches = rank_columns(
            question=question,
            table=table_match.table,
        )

        schema_matches.append(
            SchemaMatch(
                table=table_match.table,
                table_score=table_match.score,
                columns=column_matches,
            )
        )

    return schema_matches