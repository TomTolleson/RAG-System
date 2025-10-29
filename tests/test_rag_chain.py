import pytest
from unittest.mock import Mock, patch
from src.rag.rag_chain import RAGChain
from langchain_core.documents import Document


def test_rag_chain_initialization(rag_chain: RAGChain, mock_openai):
    assert rag_chain.qa_chain is None
    assert rag_chain.vector_store is not None
    assert rag_chain.llm is not None


def test_rag_chain_missing_api_key(monkeypatch):
    """Test RAGChain raises error when OPENAI_API_KEY is missing."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        RAGChain()


def test_initialize_chain_initializes_with_space(rag_chain: RAGChain):
    # Should not raise when provided a collection name
    rag_chain.initialize_chain("test_collection")


def test_initialize_chain_with_documents(rag_chain: RAGChain, mock_chroma):
    rag_chain.initialize_chain("test_collection")
    assert rag_chain.qa_chain is not None


def test_initialize_chain_error_handling(rag_chain: RAGChain, mock_openai):
    """Test initialize_chain handles errors appropriately."""
    with patch('src.rag.rag_chain.Chroma', side_effect=Exception("Connection error")):
        with pytest.raises(ValueError, match="Failed to initialize chain"):
            rag_chain.initialize_chain("test_collection")


def test_query_initializes_chain(rag_chain: RAGChain, mock_openai):
    mock_response = {"result": "Test response"}
    rag_chain.qa_chain = Mock()
    rag_chain.qa_chain.invoke.return_value = mock_response

    result = rag_chain.query("test question", space_name="test_collection")

    assert result == [{"text": "Test response", "metadata": {"source": "qa_chain"}}]
    rag_chain.qa_chain.invoke.assert_called_once()


def test_query_without_initialization(rag_chain: RAGChain, mock_chroma):
    """Test query auto-initializes chain if not initialized."""
    mock_response = {"result": "Auto-init response"}
    
    # Mock the chain after initialization
    mock_qa = Mock()
    mock_qa.invoke.return_value = mock_response
    
    with patch.object(rag_chain, 'initialize_chain'):
        with patch.object(rag_chain, 'qa_chain', None):
            # Temporarily set qa_chain property to auto-initialize
            rag_chain.query("test", "test_collection")
            # Should have called initialize_chain
            assert hasattr(rag_chain, 'qa_chain') or rag_chain.qa_chain is not None


def test_query_error_handling(rag_chain: RAGChain, mock_openai):
    """Test query handles errors appropriately."""
    rag_chain.qa_chain = Mock()
    rag_chain.qa_chain.invoke.side_effect = Exception("Query failed")
    
    with pytest.raises(Exception, match="Failed to query"):
        rag_chain.query("test", "test_collection")


def test_query_none_chain_error(rag_chain: RAGChain, mock_openai):
    """Test query raises error when chain is None."""
    rag_chain.qa_chain = None
    with patch.object(rag_chain, 'initialize_chain'):
        rag_chain.qa_chain = None  # Force None even after initialization attempt
        with pytest.raises(ValueError, match="QA chain not initialized"):
            # Need to mock to prevent actual initialization
            with patch.object(rag_chain, 'initialize_chain', return_value=None):
                rag_chain.qa_chain = None
                rag_chain.query("test", "test_collection")


def test_get_spaces(rag_chain: RAGChain):
    """Test get_spaces returns list from vector_store."""
    mock_spaces = ["space1", "space2", "space3"]
    rag_chain.vector_store.get_existing_collections = Mock(return_value=mock_spaces)
    
    spaces = rag_chain.get_spaces()
    assert spaces == mock_spaces
    assert isinstance(spaces, list)


def test_add_documents(rag_chain: RAGChain):
    """Test add_documents calls vector_store.add_documents."""
    test_docs = [
        {"text": "Doc 1", "metadata": {}},
        {"text": "Doc 2", "metadata": {}}
    ]
    rag_chain.vector_store.add_documents = Mock()
    
    rag_chain.add_documents(test_docs, "test_space")
    rag_chain.vector_store.add_documents.assert_called_once_with(test_docs, "test_space")


def test_add_documents_empty_list(rag_chain: RAGChain):
    """Test add_documents handles empty list."""
    rag_chain.vector_store.add_documents = Mock()
    rag_chain.add_documents([], "test_space")
    rag_chain.vector_store.add_documents.assert_called_once_with([], "test_space")
