import pytest
from unittest.mock import Mock
from src.rag.rag_chain import RAGChain
from langchain_core.documents import Document


def test_rag_chain_initialization(rag_chain: RAGChain, mock_openai):
    assert rag_chain.qa_chain is None
    assert rag_chain.vector_store is not None
    assert rag_chain.llm is not None


def test_initialize_chain_initializes_with_space(rag_chain: RAGChain):
    # Should not raise when provided a collection name
    rag_chain.initialize_chain("test_collection")


def test_initialize_chain_with_documents(rag_chain: RAGChain, mock_chroma):
    rag_chain.initialize_chain("test_collection")
    assert rag_chain.qa_chain is not None


def test_query_initializes_chain(rag_chain: RAGChain, mock_openai):
    mock_response = {"result": "Test response"}
    rag_chain.qa_chain = Mock()
    rag_chain.qa_chain.invoke.return_value = mock_response

    result = rag_chain.query("test question", space_name="test_collection")

    assert result == [{"text": "Test response", "metadata": {"source": "qa_chain"}}]
    rag_chain.qa_chain.invoke.assert_called_once()
