"""Build the search index: chunk documents -> embed -> store vectors in Qdrant + chunks on disk."""

import json
import time

from qdrant_client.models import Distance, PointStruct, VectorParams

from . import llm
from .chunking import chunk_markdown
from .config import Settings
from .retrieval import DOC_PREFIX, open_qdrant, point_id


def build_index(settings: Settings) -> int:
    docs = sorted(settings.docs_dir.glob("*.md"))
    if not docs:
        raise FileNotFoundError(f"No .md files in {settings.docs_dir}")

    chunks = []
    for path in docs:
        chunks.extend(chunk_markdown(path.stem, path.read_text(encoding="utf-8")))

    vectors = llm.embed(settings, [DOC_PREFIX + c.embed_text() for c in chunks])

    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    client = open_qdrant(settings)
    try:
        if client.collection_exists(settings.collection):
            client.delete_collection(settings.collection)
        client.create_collection(
            settings.collection,
            vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE),
        )
        client.upsert(
            settings.collection,
            points=[
                PointStruct(id=point_id(c.id), vector=v, payload={"chunk_id": c.id, "doc": c.doc})
                for c, v in zip(chunks, vectors)
            ],
        )
    finally:
        client.close()

    settings.chunks_file.write_text(json.dumps([c.to_dict() for c in chunks], indent=2), encoding="utf-8")
    return len(chunks)


def main() -> None:
    settings = Settings()
    start = time.perf_counter()
    n = build_index(settings)
    print(f"Indexed {n} chunks from {settings.docs_dir} in {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
