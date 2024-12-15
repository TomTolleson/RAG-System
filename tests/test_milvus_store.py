import pytest
from unittest.mock import Mock, patch
from src.vector_store.milvus_store import MilvusStore
from langchain_core.documents import Document

@pytest.fixture
def mock_embeddings():
    return Mock()

@pytest.fixture
def milvus_store(mock_embeddings):
    with patch('src.vector_store.milvus_store.OpenAIEmbeddings') as mock_openai_embeddings:
        mock_openai_embeddings.return_value = mock_embeddings
        return MilvusStore()

@pytest.fixture
def sample_documents():
    return [
        Document(page_content="Test document 1", metadata={"source": "test1"}),
        Document(page_content="Test document 2", metadata={"source": "test2"})
    ]

@pytest.fixture
def mock_milvus_connection(mocker):
    mock_conn = mocker.patch('langchain_community.vectorstores.milvus.connections.connect')
    return mock_conn

def test_milvus_store_initialization(milvus_store):
    assert milvus_store.vector_store is None
    assert milvus_store.embeddings is not None

def test_add_documents(milvus_store, sample_documents, mock_milvus):
    result = milvus_store.add_documents(sample_documents)
    assert result == mock_milvus

def test_similarity_search_without_documents(milvus_store):
    with pytest.raises(ValueError, match="No documents have been added to the vector store"):
        milvus_store.similarity_search("test query")

def test_similarity_search_with_documents(milvus_store):
    mock_vector_store = Mock()
    expected_results = [Document(page_content="Test result")]
    mock_vector_store.similarity_search.return_value = expected_results
    milvus_store.vector_store = mock_vector_store
    
    results = milvus_store.similarity_search("test query", k=4)
    
    assert results == expected_results
    mock_vector_store.similarity_search.assert_called_once_with("test query", k=4)
