import re


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9_ ]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()

# score the column name based on question
def score_name(
    question: str,
    name: str,
    synonyms: list[str],
) -> float:
    normalized_question = normalize_text(question)
    normalized_name = normalize_text(name)

    if normalized_name in normalized_question:
        return 1.0

    for synonym in synonyms:
        normalized_synonym = normalize_text(synonym)

        if normalized_synonym in normalized_question:
            return 1.0

    return 0.0

