"""Scoring helpers for the evaluation suite."""

import re


def normalize(text: str) -> str:
    """Lowercase, drop thousands separators and the rupee sign, collapse whitespace."""
    text = text.lower().replace("₹", "rs ")
    text = re.sub(r"(?<=\d),(?=\d)", "", text)
    return re.sub(r"\s+", " ", text)


def contains_facts(answer: str, must_include: list[list[str]]) -> bool:
    """Each inner list is a group of acceptable alternatives; every group must match."""
    norm = normalize(answer)
    return all(any(normalize(alt) in norm for alt in group) for group in must_include)


def reciprocal_rank(retrieved_docs: list[str], expected_doc: str) -> float:
    for rank, doc in enumerate(retrieved_docs, start=1):
        if doc == expected_doc:
            return 1.0 / rank
    return 0.0
