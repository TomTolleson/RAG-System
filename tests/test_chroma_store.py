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


def test_get_existing_collections(chroma_store, mocker):
    """Test get_existing_collections returns list of collections."""
    mock_client = Mock()
    mock_collections = ["collection1", "collection2"]
    mock_client.list_collections.return_value = [Mock(name=c) for c in mock_collections]
    mocker.patch.object(chroma_store, "_chroma_client", mock_client)
    
    collections = chroma_store.get_existing_collections()
    assert isinstance(collections, list)


def test_delete_collection(chroma_store, mocker):
    """Test delete_collection removes a collection."""
    mock_client = Mock()
    mock_client.delete_collection = Mock()
    mocker.patch.object(chroma_store, "_chroma_client", mock_client)
    
    chroma_store.delete_collection("test_collection")
    mock_client.delete_collection.assert_called_once()


def test_add_documents_empty_list(chroma_store):
    """Test add_documents handles empty document list."""
    result = chroma_store.add_documents([], "test_collection")
    assert result is None


def test_add_documents_error_handling(chroma_store, sample_documents, mocker):
    """Test add_documents handles errors gracefully."""
    mock_collection = Mock()
    mock_collection.add.side_effect = Exception("Storage error")
    mock_client = Mock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mocker.patch.object(chroma_store, "_chroma_client", mock_client)
    
    with pytest.raises(Exception):
        chroma_store.add_documents(sample_documents, "test_collection")


def test_similarity_search_empty_query(chroma_store):
    """Test similarity_search handles empty query."""
    results = chroma_store.similarity_search("", "test_collection")
    assert isinstance(results, list)


def test_similarity_search_different_k_values(chroma_store, mocker):
    """Test similarity_search with different k values."""
    mock_collection = Mock()
    mock_collection.query.return_value = {
        "documents": [["Doc 1", "Doc 2", "Doc 3"]],
        "metadatas": [[{}, {}, {}]],
        "distances": [[0.1, 0.2, 0.3]],
    }
    mock_client = Mock()
    mock_client.get_collection.return_value = mock_collection
    mocker.patch.object(chroma_store, "_chroma_client", mock_client)
    
    results_k1 = chroma_store.similarity_search("query", "test_collection", k=1)
    assert len(results_k1) == 1
    
    results_k3 = chroma_store.similarity_search("query", "test_collection", k=3)
    assert len(results_k3) == 3
