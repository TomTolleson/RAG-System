import pytest
from src.vector_store.chroma_store import ChromaStore
from langchain.schema import Document


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
    with pytest.raises(Exception):
        chroma_store.similarity_search("test query", "non_existent_collection")


def test_similarity_search_with_documents(chroma_store, mock_chroma):
    expected_results = [
        {"text": "Test document 1", "metadata": {"source": "test1"}, "score": 0.9},
        {"text": "Test document 2", "metadata": {"source": "test2"}, "score": 0.8}
    ]
    mock_chroma.similarity_search.return_value = expected_results
    results = chroma_store.similarity_search("test query", "test_collection", k=4)
    assert results == expected_results

