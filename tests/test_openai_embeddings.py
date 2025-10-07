import pytest


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")


def test_openai_embeddings_calls_client(mocker):
    mock_client = mocker.Mock()
    # Mock response structure
    mock_client.embeddings.create.return_value = mocker.Mock(
        data=[mocker.Mock(embedding=[0.1, 0.2, 0.3])]
    )

    mock_openai_cls = mocker.patch('src.embeddings.openai_embeddings.OpenAI', return_value=mock_client)

    from src.embeddings.openai_embeddings import OpenAIEmbeddings

    emb = OpenAIEmbeddings(api_key="test-key")
    # __call__ path (single string)
    out = emb("hello")
    assert out == [[0.1, 0.2, 0.3]]
    # embed_documents path
    out_docs = emb.embed_documents(["a", "b"])
    assert out_docs == [[0.1, 0.2, 0.3]]
    # embed_query path
    out_q = emb.embed_query("hello")
    assert out_q == [0.1, 0.2, 0.3]

    assert mock_openai_cls.called
    assert mock_client.embeddings.create.call_count >= 3

