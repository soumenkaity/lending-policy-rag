"""Answer generation: retrieved excerpts -> grounded answer with [n] citations, or an explicit refusal."""

import re
import time
from dataclasses import dataclass, field

from . import llm
from .chunking import Chunk
from .config import Settings
from .retrieval import Retriever

REFUSAL_TOKEN = "NOT_IN_POLICY"
REFUSAL_MESSAGE = "I couldn't find this in the Northwind Credit policy documents. Please contact support."

SYSTEM_PROMPT = f"""You are a lending-policy assistant for Northwind Credit.
Answer the user's question using ONLY the numbered policy excerpts provided. Users write in everyday
language, so match their words to the policy terms by meaning, not by exact wording.

Respond in exactly this format:
EVIDENCE: the sentence(s) copied word for word from the excerpts that answer the question, each followed by its excerpt number, e.g. [2]
ANSWER: a concise answer (1 to 3 sentences) with exact numbers, amounts and time limits, citing excerpt numbers like [2]

If no excerpt contains evidence about the topic asked (for example a product, person or payment method
the excerpts never mention), respond with exactly: {REFUSAL_TOKEN}
Never use outside knowledge and never guess."""


def build_user_message(question: str, chunks: list[Chunk]) -> str:
    excerpts = "\n\n".join(
        f"[{i}] {c.title} > {c.section}\n{c.text}" for i, c in enumerate(chunks, start=1)
    )
    return f"Policy excerpts:\n\n{excerpts}\n\nQuestion: {question}"


def parse_citations(text: str, n_sources: int) -> list[int]:
    found = {int(m) for group in re.findall(r"\[([\d,\s]+)\]", text) for m in re.findall(r"\d+", group)}
    return sorted(i for i in found if 1 <= i <= n_sources)


@dataclass
class Answer:
    question: str
    text: str
    answered: bool
    sources: list[Chunk]
    cited: list[int] = field(default_factory=list)
    latency_ms: int = 0


def answer_question(question: str, retriever: Retriever, settings: Settings) -> Answer:
    start = time.perf_counter()
    chunks = retriever.search(question)
    raw = llm.chat(
        settings,
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(question, chunks)},
        ],
    ).strip()
    latency = int((time.perf_counter() - start) * 1000)

    if REFUSAL_TOKEN in raw:
        return Answer(question, REFUSAL_MESSAGE, False, chunks, [], latency)
    evidence, text = split_evidence(raw)
    return Answer(question, text, True, chunks, parse_citations(evidence + " " + text, len(chunks)), latency)


def split_evidence(raw: str) -> tuple[str, str]:
    """Split 'EVIDENCE: ... ANSWER: ...' into its parts. Falls back to the whole text as the answer."""
    match = re.search(r"ANSWER:\s*(.*)", raw, flags=re.S | re.I)
    if not match:
        return "", raw
    evidence = re.sub(r"^\s*EVIDENCE:\s*", "", raw[: match.start()], flags=re.I).strip()
    return evidence, match.group(1).strip()
