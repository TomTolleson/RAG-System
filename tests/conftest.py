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

    # Create a mock Chroma-like vectorstore with an as_retriever method
    mock_vectorstore = Mock()
    mock_vectorstore.as_retriever.return_value = mock_retriever

    # Patch the LangChain Chroma class used inside RAGChain.initialize_chain
    mocker.patch('src.rag.rag_chain.Chroma', return_value=mock_vectorstore)

    return mock_vectorstore


@pytest.fixture
def mock_openai(mocker, mock_openai_key) -> dict[str, Union[Mock, Mock]]:
    # Mock ChatOpenAI used in RAGChain
    mock_chat = create_autospec(ChatOpenAI, instance=True)
    mock_chat.invoke.return_value = {"result": "test response"}

    # Provide an embedding function with the correct __call__(input) signature
    class DummyEmbeddings:
        def __call__(self, input):
            if isinstance(input, list):
                return [[0.1, 0.2, 0.3] for _ in input]
            return [[0.1, 0.2, 0.3]]

        def embed_documents(self, texts):
            return [[0.1, 0.2, 0.3] for _ in texts]

        def embed_query(self, text):
            return [0.1, 0.2, 0.3]

    mock_embeddings = DummyEmbeddings()

    # Patch classes to return our mocks
    mocker.patch('src.vector_store.chroma_store.OpenAIEmbeddings', return_value=mock_embeddings)
    mocker.patch('src.rag.rag_chain.ChatOpenAI', return_value=mock_chat)

    return {'embeddings': mock_embeddings, 'chat': mock_chat}


@pytest.fixture
def chroma_store(mock_openai) -> ChromaStore:
    return ChromaStore()


@pytest.fixture
def rag_chain(mock_openai, mock_chroma) -> RAGChain:
    return RAGChain()
