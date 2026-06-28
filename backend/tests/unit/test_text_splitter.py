from app.rag.text_splitter import split_text


def test_split_text_keeps_order_and_overlap():
    text = "0123456789" * 30

    chunks = split_text(text, chunk_size=100, chunk_overlap=10)

    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))
    assert len(chunks) > 1
    assert chunks[0].chunk_text[-10:] == chunks[1].chunk_text[:10]
