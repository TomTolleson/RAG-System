import pytest
from unittest.mock import Mock, patch
from src.rag.rag_chain import RAGChain
from langchain_core.documents import Document

@pytest.fixture
def mock_vector_store():
    mock = Mock()
    mock.vector_store = Mock()
    mock.vector_store.as_retriever.return_value = Mock()
    return mock

@pytest.fixture
def mock_llm():
    return Mock()

@pytest.fixture
def rag_chain(mock_vector_store, mock_llm):
    with patch('src.rag.rag_chain.MilvusStore') as mock_milvus_store, \
         patch('src.rag.rag_chain.ChatOpenAI') as mock_chat_openai:
        mock_milvus_store.return_value = mock_vector_store
        mock_chat_openai.return_value = mock_llm
        return RAGChain()

def test_rag_chain_initialization(rag_chain):
    assert rag_chain.qa_chain is None
    assert rag_chain.vector_store is not None
    assert rag_chain.llm is not None

def test_initialize_chain_without_documents(rag_chain):
    rag_chain.vector_store.vector_store = None
    with pytest.raises(ValueError, match="Vector store has not been initialized with documents"):
        rag_chain.initialize_chain()

def test_initialize_chain_with_documents(rag_chain):
    rag_chain.initialize_chain()
    assert rag_chain.qa_chain is not None

def test_query_initializes_chain(rag_chain):
    mock_response = {"result": "Test response"}
    rag_chain.qa_chain = Mock()
    rag_chain.qa_chain.invoke.return_value = mock_response
    
    result = rag_chain.query("test question")
    
    assert result == "Test response"
    rag_chain.qa_chain.invoke.assert_called_once_with({"query": "test question"})
