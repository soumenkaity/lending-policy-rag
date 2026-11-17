from pathlib import Path

from lendrag.chunking import chunk_markdown

DOC = """# Fee Policy

Intro paragraph.

## Processing Fee

Two percent.

## Late Fee

Five hundred rupees.
"""


def test_sections_become_chunks():
    chunks = chunk_markdown("04-fees", DOC)
    assert [c.section for c in chunks] == ["Overview", "Processing Fee", "Late Fee"]
    assert all(c.title == "Fee Policy" for c in chunks)
    assert chunks[1].id == "04-fees#processing-fee"
    assert chunks[1].embed_text().startswith("Fee Policy > Processing Fee")


def test_long_sections_split_on_paragraphs():
    long_doc = "# T\n\n## Big\n\n" + "\n\n".join(["word " * 50] * 6)
    chunks = chunk_markdown("d", long_doc, max_chars=600)
    assert len(chunks) > 1
    assert all(len(c.text) <= 600 for c in chunks)
    assert len({c.id for c in chunks}) == len(chunks)


def test_real_policies_have_unique_ids():
    docs = Path(__file__).parents[1] / "data" / "policies"
    chunks = [c for p in sorted(docs.glob("*.md")) for c in chunk_markdown(p.stem, p.read_text(encoding="utf-8"))]
    assert len(chunks) >= 25
    assert len({c.id for c in chunks}) == len(chunks)
