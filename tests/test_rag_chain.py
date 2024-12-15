import pytest
from unittest.mock import Mock
from src.rag.rag_chain import RAGChain


def test_rag_chain_initialization(rag_chain: RAGChain, mock_openai):
    assert rag_chain.qa_chain is None
    assert rag_chain.vector_store is not None
    assert rag_chain.llm is not None


def test_initialize_chain_without_documents(rag_chain: RAGChain):
    rag_chain.vector_store.vector_store = None
    with pytest.raises(ValueError, match="Vector store has not been initialized with documents"):
        rag_chain.initialize_chain()


def test_initialize_chain_with_documents(rag_chain: RAGChain):
    rag_chain.initialize_chain()
    assert rag_chain.qa_chain is not None


def test_query_initializes_chain(rag_chain: RAGChain, mock_milvus, mock_openai):
    mock_response = {"result": "Test response"}
    rag_chain.qa_chain = Mock()
    rag_chain.qa_chain.invoke.return_value = mock_response
    
    result = rag_chain.query("test question")
    
    assert result == "Test response"
    rag_chain.qa_chain.invoke.assert_called_once()