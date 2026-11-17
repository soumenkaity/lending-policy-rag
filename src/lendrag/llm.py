"""Thin HTTP clients for embeddings and chat. No framework: every request is visible here."""

import httpx

from .config import Settings


class LLMError(RuntimeError):
    pass


def embed(settings: Settings, texts: list[str]) -> list[list[float]]:
    try:
        r = httpx.post(
            f"{settings.ollama_url}/api/embed",
            json={"model": settings.embed_model, "input": texts},
            timeout=300,
        )
        r.raise_for_status()
    except httpx.HTTPError as e:
        raise LLMError(f"Embedding call to Ollama failed ({e}). Is Ollama running?") from e
    return r.json()["embeddings"]


def chat(settings: Settings, messages: list[dict]) -> str:
    try:
        if settings.llm_provider == "ollama":
            r = httpx.post(
                f"{settings.ollama_url}/api/chat",
                json={
                    "model": settings.chat_model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0, "num_ctx": 4096},
                },
                timeout=300,
            )
            r.raise_for_status()
            return r.json()["message"]["content"]

        if settings.llm_provider == "openai":
            r = httpx.post(
                f"{settings.openai_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": settings.chat_model, "messages": messages, "temperature": 0},
                timeout=120,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except httpx.HTTPError as e:
        raise LLMError(f"Chat call failed ({e})") from e

    raise LLMError(f"Unknown LLM_PROVIDER '{settings.llm_provider}' (use 'ollama' or 'openai')")
