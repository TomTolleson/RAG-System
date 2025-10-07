import pytest
from unittest.mock import Mock


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")


def test_embedding_handler_initializes_embeddings(mocker):
    mock_embeddings = Mock()
    mocker.patch('src.embeddings.embedding_handler.OpenAIEmbeddings', return_value=mock_embeddings)

    from src.embeddings.embedding_handler import EmbeddingHandler

    handler = EmbeddingHandler()
    assert handler.get_embeddings() is mock_embeddings

