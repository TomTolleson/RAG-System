import pytest
from pathlib import Path
import tempfile
from unittest.mock import Mock


@pytest.fixture
def temp_document():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document about Milvus.")
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()  # Cleanup after test


@pytest.fixture
def mock_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")


@pytest.fixture
def mock_milvus(mocker):
    # Mock the entire Milvus connection and operations
    mocker.patch('pymilvus.connections.connect')
    mock_milvus = Mock()
    mocker.patch('langchain_community.vectorstores.milvus.Milvus.from_documents', return_value=mock_milvus)
    return mock_milvus


@pytest.fixture
def mock_openai(mocker):
    # Mock OpenAI embeddings and chat
    mock_embeddings = Mock()
    mock_chat = Mock()
    mocker.patch('src.vector_store.milvus_store.OpenAIEmbeddings', return_value=mock_embeddings)
    mocker.patch('src.rag.rag_chain.ChatOpenAI', return_value=mock_chat)
    return {'embeddings': mock_embeddings, 'chat': mock_chat}