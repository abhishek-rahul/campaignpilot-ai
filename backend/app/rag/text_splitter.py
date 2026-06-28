from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    chunk_text: str
    token_count: int


def split_text(text: str, *, chunk_size: int = 1000, chunk_overlap: int = 150) -> list[TextChunk]:
    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not cleaned:
        return []
    if chunk_overlap >= chunk_size:
        chunk_overlap = max(0, chunk_size // 5)

    chunks: list[TextChunk] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunk_text = cleaned[start:end].strip()
        if chunk_text:
            chunks.append(
                TextChunk(
                    chunk_index=len(chunks),
                    chunk_text=chunk_text,
                    token_count=max(1, len(chunk_text.split())),
                )
            )
        if end >= len(cleaned):
            break
        start = max(0, end - chunk_overlap)
    return chunks
