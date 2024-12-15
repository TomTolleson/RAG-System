import pytest
from pathlib import Path
import tempfile
from unittest.mock import Mock, create_autospec
from typing import Generator, Union
from src.vector_store.milvus_store import MilvusStore
from src.rag.rag_chain import RAGChain
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Milvus
from langchain_core.retrievers import BaseRetriever


@pytest.fixture
def temp_document() -> Generator[Path, None, None]:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document about Milvus.")
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()  # Cleanup after test


@pytest.fixture
def mock_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")


@pytest.fixture
def mock_milvus(mocker) -> Mock:
    # Create a mock retriever that implements the BaseRetriever interface
    mock_retriever = create_autospec(BaseRetriever, instance=True)
    mock_retriever.get_relevant_documents.return_value = []
    
    # Create a mock Milvus instance
    mock_milvus = create_autospec(Milvus, instance=True)
    mock_milvus.as_retriever.return_value = mock_retriever
    
    # Patch the Milvus connection
    mocker.patch('pymilvus.connections.connect')
    mocker.patch('langchain_community.vectorstores.milvus.Milvus.from_documents', return_value=mock_milvus)
    
    return mock_milvus


@pytest.fixture
def mock_openai(mocker) -> dict[str, Union[Mock, Mock]]:
    # Create a proper mock that mimics ChatOpenAI
    mock_chat = create_autospec(ChatOpenAI, instance=True)
    mock_chat.invoke.return_value = {"response": "test response"}
    
    mock_embeddings = Mock()
    
    # Update the patches to use the autospec'd mock
    mocker.patch('src.vector_store.milvus_store.OpenAIEmbeddings', return_value=mock_embeddings)
    mocker.patch('src.rag.rag_chain.ChatOpenAI', return_value=mock_chat)
    
    return {'embeddings': mock_embeddings, 'chat': mock_chat}


@pytest.fixture
def milvus_store(mock_openai) -> MilvusStore:
    return MilvusStore()


@pytest.fixture
def rag_chain(mock_openai, mock_milvus) -> RAGChain:
    return RAGChain()