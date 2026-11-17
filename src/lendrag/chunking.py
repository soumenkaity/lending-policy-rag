"""Split markdown policy documents into section-level chunks.

Policy documents are written as one rule per "## " section, so a section is the natural
retrieval unit: small enough to be precise, large enough to keep a rule and its exceptions together.
Very long sections are split further on paragraph boundaries.
"""

import re
from dataclasses import asdict, dataclass


@dataclass
class Chunk:
    id: str
    doc: str  # file stem, e.g. "03-disbursement"
    title: str  # document title, e.g. "Disbursement Policy"
    section: str  # section heading, e.g. "Failed Disbursements"
    text: str

    def embed_text(self) -> str:
        """Text used for embeddings and keyword search: the headings carry a lot of meaning."""
        return f"{self.title} > {self.section}\n{self.text}"

    def to_dict(self) -> dict:
        return asdict(self)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _split_long(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    parts, current = [], ""
    for para in text.split("\n\n"):
        if current and len(current) + len(para) + 2 > max_chars:
            parts.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        parts.append(current)
    return parts


def chunk_markdown(doc: str, markdown: str, max_chars: int = 1200) -> list[Chunk]:
    title = doc
    sections: list[tuple[str, list[str]]] = [("Overview", [])]
    for line in markdown.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            sections.append((line[3:].strip(), []))
        else:
            sections[-1][1].append(line)

    chunks: list[Chunk] = []
    for section, lines in sections:
        body = "\n".join(lines).strip()
        if not body:
            continue
        pieces = _split_long(body, max_chars)
        for i, piece in enumerate(pieces):
            suffix = f"-{i + 1}" if len(pieces) > 1 else ""
            chunks.append(Chunk(f"{doc}#{_slug(section)}{suffix}", doc, title, section, piece))
    return chunks
