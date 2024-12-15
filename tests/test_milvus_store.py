import pytest
from langchain_core.documents import Document


@pytest.fixture
def sample_documents():
    return [
        Document(page_content="Test document 1", metadata={"source": "test1"}),
        Document(page_content="Test document 2", metadata={"source": "test2"})
    ]


def test_milvus_store_initialization(milvus_store, mock_openai):
    assert milvus_store.vector_store is None
    assert milvus_store.embeddings is not None


def test_add_documents(milvus_store, sample_documents, mock_milvus):
    result = milvus_store.add_documents(sample_documents)
    assert result == mock_milvus


def test_similarity_search_without_documents(milvus_store):
    with pytest.raises(
        ValueError,
        match="No documents have been added to the vector store"
    ):
        milvus_store.similarity_search("test query")


def test_similarity_search_with_documents(milvus_store, mock_milvus):
    expected_results = [Document(page_content="Test result")]
    mock_milvus.similarity_search.return_value = expected_results
    milvus_store.vector_store = mock_milvus
    results = milvus_store.similarity_search("test query", k=4)
    assert results == expected_results
    mock_milvus.similarity_search.assert_called_once_with("test query", k=4)

