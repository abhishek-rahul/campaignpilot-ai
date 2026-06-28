from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from app.core.config import settings
from app.llm.llm_client import should_use_mock

MOCK_EMBEDDING_DIMENSION = 384


@dataclass(frozen=True)
class EmbeddingResult:
    embeddings: list[list[float]]
    provider: str
    model_name: str
    vector_dimension: int
    used_mock: bool


def embed_texts(texts: list[str], model_name: str | None = None) -> EmbeddingResult:
    if should_use_mock():
        vectors = [_mock_embedding(text) for text in texts]
        return EmbeddingResult(
            embeddings=vectors,
            provider="mock",
            model_name="mock-hash-embedding",
            vector_dimension=MOCK_EMBEDDING_DIMENSION,
            used_mock=True,
        )

    from openai import OpenAI

    model = model_name or settings.openai_embedding_model
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(model=model, input=texts)
    vectors = [item.embedding for item in response.data]
    dimension = len(vectors[0]) if vectors else 0
    return EmbeddingResult(
        embeddings=vectors,
        provider="openai",
        model_name=model,
        vector_dimension=dimension,
        used_mock=False,
    )


def embed_query(text: str, model_name: str | None = None) -> EmbeddingResult:
    return embed_texts([text], model_name=model_name)


def _mock_embedding(text: str) -> list[float]:
    vector = [0.0] * MOCK_EMBEDDING_DIMENSION
    words = [word.strip().lower() for word in text.split() if word.strip()]
    for word in words or [text.lower()]:
        digest = hashlib.sha256(word.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:4], "big") % MOCK_EMBEDDING_DIMENSION
        sign = -1.0 if digest[4] % 2 else 1.0
        vector[bucket] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 6) for value in vector]
