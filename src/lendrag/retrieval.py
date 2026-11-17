"""Hybrid retrieval: semantic vector search (Qdrant) + keyword search (BM25), fused with RRF.

Why hybrid? Vector search understands paraphrases ("pay off early" ~ "foreclosure"), while BM25
nails exact terms that embeddings blur, such as "FOIR", "penny-drop" or "SMA-1". Reciprocal Rank
Fusion merges the two ranked lists without having to calibrate their very different scores.
"""

import json
import re
import uuid

from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi

from . import llm
from .chunking import Chunk
from .config import Settings

QUERY_PREFIX = "search_query: "  # nomic-embed-text expects task prefixes
DOC_PREFIX = "search_document: "

REWRITE_PROMPT = (
    "Rewrite the customer's question as one short search query using the formal banking terms that a "
    "lender's written loan policy would use for the same concept. Output only the query."
)

_STOPWORDS = set(
    "a an and are as at be by can do does for from how i if in is it its me my of on or the "
    "there this to was what when where which who will with you your".split()
)
_TOKEN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOPWORDS]


def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion: score(d) = sum over lists of 1 / (k + rank)."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def open_qdrant(settings: Settings) -> QdrantClient:
    if settings.qdrant_url:
        return QdrantClient(url=settings.qdrant_url)
    return QdrantClient(path=str(settings.storage_dir / "qdrant"))


class Retriever:
    def __init__(self, settings: Settings):
        if not settings.chunks_file.exists():
            raise FileNotFoundError(f"No index at {settings.storage_dir}. Run `uv run lendrag-ingest` first.")
        self.settings = settings
        self.chunks = [Chunk(**c) for c in json.loads(settings.chunks_file.read_text(encoding="utf-8"))]
        self.by_id = {c.id: c for c in self.chunks}
        self.bm25 = BM25Okapi([tokenize(c.embed_text()) for c in self.chunks])
        self.qdrant = open_qdrant(settings)

    def vector_search(self, query: str, k: int) -> list[str]:
        vector = llm.embed(self.settings, [QUERY_PREFIX + query])[0]
        hits = self.qdrant.query_points(self.settings.collection, query=vector, limit=k).points
        return [hit.payload["chunk_id"] for hit in hits]

    def bm25_search(self, query: str, k: int) -> list[str]:
        scores = self.bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [self.chunks[i].id for i in order[:k] if scores[i] > 0]

    def rewrite_query(self, query: str) -> str:
        """Ask the LLM to restate the question in the formal vocabulary policy documents use."""
        return llm.chat(
            self.settings,
            [
                {"role": "system", "content": REWRITE_PROMPT},
                {"role": "user", "content": query},
            ],
        ).strip()

    def search(self, query: str, k: int | None = None, mode: str | None = None) -> list[Chunk]:
        k = k or self.settings.top_k
        mode = mode or self.settings.retrieval_mode
        candidates = max(k * 2, 8)
        if mode == "vector":
            ids = self.vector_search(query, k)
        elif mode == "bm25":
            ids = self.bm25_search(query, k)
        elif mode in ("hybrid", "hybrid+rewrite"):
            queries = [query]
            if mode == "hybrid+rewrite":
                queries.append(self.rewrite_query(query))
            rankings = []
            for q in queries:
                rankings += [self.vector_search(q, candidates), self.bm25_search(q, candidates)]
            ids = [doc_id for doc_id, _ in rrf(rankings)[:k]]
        else:
            raise ValueError(f"unknown mode {mode}")
        return [self.by_id[i] for i in ids]

    def close(self) -> None:
        self.qdrant.close()
