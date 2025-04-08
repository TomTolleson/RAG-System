import pytest
from pathlib import Path
import tempfile
from unittest.mock import Mock, create_autospec
from typing import Generator, Union
from src.vector_store.chroma_store import ChromaStore
from src.rag.rag_chain import RAGChain
from langchain_openai import ChatOpenAI
from langchain_core.retrievers import BaseRetriever


@pytest.fixture
def temp_document() -> Generator[Path, None, None]:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document.")
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()  # Cleanup after test


@pytest.fixture
def mock_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")


@pytest.fixture
def mock_chroma(mocker) -> Mock:
    # Create a mock retriever that implements the BaseRetriever interface
    mock_retriever = create_autospec(BaseRetriever, instance=True)
    mock_retriever.get_relevant_documents.return_value = []
    
    # Create a mock ChromaDB instance
    mock_chroma = create_autospec(ChromaStore, instance=True)
    mock_chroma.as_retriever.return_value = mock_retriever
    
    return mock_chroma


@pytest.fixture
def mock_openai(mocker) -> dict[str, Union[Mock, Mock]]:
    # Create a proper mock that mimics ChatOpenAI
    mock_chat = create_autospec(ChatOpenAI, instance=True)
    mock_chat.invoke.return_value = {"response": "test response"}
    
    mock_embeddings = Mock()
    
    # Update the patches to use the autospec'd mock
    mocker.patch('src.vector_store.chroma_store.OpenAIEmbeddingFunction', return_value=mock_embeddings)
    mocker.patch('src.rag.rag_chain.ChatOpenAI', return_value=mock_chat)
    
    return {'embeddings': mock_embeddings, 'chat': mock_chat}


@pytest.fixture
def chroma_store(mock_openai) -> ChromaStore:
    return ChromaStore()


@pytest.fixture
def rag_chain(mock_openai, mock_chroma) -> RAGChain:
    return RAGChain()