"""All settings come from environment variables so the same code runs locally, in Docker and in CI."""

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    docs_dir: Path = field(default_factory=lambda: Path(_env("DOCS_DIR", str(ROOT / "data" / "policies"))))
    storage_dir: Path = field(default_factory=lambda: Path(_env("STORAGE_DIR", str(ROOT / "storage"))))

    # Chat model: "ollama" (local, free) or "openai" (any OpenAI-compatible API: OpenAI, Groq, Together...)
    llm_provider: str = field(default_factory=lambda: _env("LLM_PROVIDER", "ollama"))
    chat_model: str = field(default_factory=lambda: _env("CHAT_MODEL", "qwen2.5:7b"))
    openai_base_url: str = field(default_factory=lambda: _env("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    openai_api_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY", ""))

    # Embeddings always come from Ollama (free, local).
    ollama_url: str = field(default_factory=lambda: _env("OLLAMA_URL", "http://localhost:11434"))
    embed_model: str = field(default_factory=lambda: _env("EMBED_MODEL", "nomic-embed-text"))

    # Empty QDRANT_URL = embedded Qdrant stored on disk, no server needed.
    qdrant_url: str = field(default_factory=lambda: _env("QDRANT_URL", ""))
    collection: str = field(default_factory=lambda: _env("QDRANT_COLLECTION", "lending_policies"))

    top_k: int = field(default_factory=lambda: int(_env("TOP_K", "4")))
    # bm25 | vector | hybrid | hybrid+rewrite (LLM rewrites the question into policy terms first)
    retrieval_mode: str = field(default_factory=lambda: _env("RETRIEVAL_MODE", "hybrid+rewrite"))
    @property
    def chunks_file(self) -> Path:
        return self.storage_dir / "chunks.json"
