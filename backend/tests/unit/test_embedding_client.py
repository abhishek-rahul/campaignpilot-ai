from app.rag.embedding_client import MOCK_EMBEDDING_DIMENSION, embed_texts


def test_mock_embeddings_are_deterministic(monkeypatch):
    monkeypatch.setattr("app.llm.llm_client.settings.openai_api_key", "replace_me")
    first = embed_texts(["brand voice friendly"])
    second = embed_texts(["brand voice friendly"])

    assert first.used_mock is True
    assert first.vector_dimension == MOCK_EMBEDDING_DIMENSION
    assert first.embeddings == second.embeddings
