import pytest
from unittest.mock import Mock
from src.vector_store.chroma_store import ChromaStore
from langchain_core.documents import Document


@pytest.fixture
def sample_documents() -> list[Document]:
    return [
        Document(page_content="Test document 1", metadata={"source": "test1"}),
        Document(page_content="Test document 2", metadata={"source": "test2"})
    ]


def test_chroma_store_initialization(chroma_store, mock_openai):
    assert chroma_store._chroma_client is not None
    assert chroma_store._embedding_function is not None


def test_add_documents(chroma_store, sample_documents, mock_chroma):
    result = chroma_store.add_documents(sample_documents, "test_collection")
    assert result is None  # add_documents doesn't return anything


def test_similarity_search_without_documents(chroma_store):
    # When collection doesn't exist, implementation returns empty list
    results = chroma_store.similarity_search("test query", "non_existent_collection")
    assert results == []


def test_similarity_search_with_documents(chroma_store, mocker):
    # Mock the internal chroma client and collection behavior
    mock_collection = Mock()
    mock_collection.query.return_value = {
        "documents": [["Test document 1", "Test document 2"]],
        "metadatas": [[{"source": "test1"}, {"source": "test2"}]],
        "distances": [[0.1, 0.2]],
    }
    mock_client = Mock()
    mock_client.get_collection.return_value = mock_collection
    mocker.patch.object(chroma_store, "_chroma_client", mock_client)

    results = chroma_store.similarity_search("test query", "test_collection", k=2)
    assert len(results) == 2
    assert results[0]["text"] == "Test document 1"
    assert results[0]["metadata"] == {"source": "test1"}

