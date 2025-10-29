"""Tests for the FastAPI application endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def mock_openai_key(monkeypatch):
    """Set up a mock OpenAI API key."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")


@pytest.fixture
def mock_rag_chain():
    """Create a mock RAGChain."""
    mock_chain = Mock()
    mock_chain.get_spaces.return_value = ["default", "test-space"]
    mock_chain.query.return_value = [{"text": "Test response", "metadata": {}}]
    mock_chain.add_documents.return_value = None
    mock_chain.initialize_chain.return_value = None
    mock_chain.vector_store = Mock()
    mock_chain.vector_store.delete_collection.return_value = None
    return mock_chain


@pytest.fixture
def client(mock_openai_key, mock_rag_chain):
    """Create a test client with mocked dependencies."""
    with patch('src.api.main.RAGChain', return_value=mock_rag_chain):
        from src.api.main import app
        return TestClient(app), mock_rag_chain


def test_health_check_success(client):
    """Test health check endpoint returns healthy status."""
    test_client, mock_chain = client
    response = test_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "collections" in data


def test_health_check_unhealthy(client, monkeypatch):
    """Test health check endpoint handles errors gracefully."""
    test_client, mock_chain = client
    # Need to patch at the app level since rag_chain is initialized at module level
    with patch('src.api.main.rag_chain.get_spaces', side_effect=Exception("Connection failed")):
        response = test_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data


def test_list_spaces_success(client):
    """Test listing spaces endpoint."""
    test_client, mock_chain = client
    response = test_client.get("/spaces")
    assert response.status_code == 200
    data = response.json()
    assert "spaces" in data
    assert isinstance(data["spaces"], list)


def test_list_spaces_error(client):
    """Test listing spaces endpoint handles errors."""
    test_client, mock_chain = client
    with patch('src.api.main.rag_chain.get_spaces', side_effect=Exception("Database error")):
        response = test_client.get("/spaces")
        assert response.status_code == 500


def test_create_space_success(client):
    """Test creating a new space."""
    test_client, mock_chain = client
    payload = {
        "name": "new-space",
        "documents": [
            {"text": "Test document", "metadata": {}}
        ]
    }
    with patch('src.api.main.rag_chain.add_documents') as mock_add, \
         patch('src.api.main.rag_chain.initialize_chain') as mock_init:
        response = test_client.post("/spaces", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "new-space" in data["message"]
        mock_add.assert_called_once()
        mock_init.assert_called_once_with("new-space")


def test_create_space_error(client):
    """Test creating space handles errors."""
    test_client, mock_chain = client
    payload = {
        "name": "new-space",
        "documents": [{"text": "Test", "metadata": {}}]
    }
    with patch('src.api.main.rag_chain.add_documents', side_effect=Exception("Storage error")):
        response = test_client.post("/spaces", json=payload)
        assert response.status_code == 500


def test_query_space_success(client):
    """Test querying a space."""
    test_client, mock_chain = client
    payload = {
        "query": "What is this about?",
        "space_name": "test-space"
    }
    with patch('src.api.main.rag_chain.query', return_value=[{"text": "Test response", "metadata": {}}]) as mock_query:
        response = test_client.post("/spaces/test-space/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0
        mock_query.assert_called_once()


def test_query_space_error(client):
    """Test query endpoint handles errors."""
    test_client, mock_chain = client
    payload = {
        "query": "Test query",
        "space_name": "test-space"
    }
    with patch('src.api.main.rag_chain.query', side_effect=Exception("Query failed")):
        response = test_client.post("/spaces/test-space/query", json=payload)
        assert response.status_code == 500


def test_upload_document_success(client):
    """Test uploading a document to a space."""
    test_client, mock_chain = client
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test document content")
        temp_path = Path(f.name)
    
    try:
        # Create space directory
        space_dir = Path("data") / "test-space"
        space_dir.mkdir(parents=True, exist_ok=True)
        
        with patch('src.api.main.DocumentLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            mock_doc = Mock()
            mock_doc.page_content = "Test content"
            mock_doc.metadata = {}
            mock_loader.load_documents.return_value = [mock_doc]
            
            with patch('src.api.main.rag_chain.add_documents') as mock_add:
                with open(temp_path, 'rb') as file:
                    files = {'file': ('test.txt', file, 'text/plain')}
                    response = test_client.post("/api/spaces/test-space/documents", files=files)
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            mock_add.assert_called_once()
    finally:
        if temp_path.exists():
            temp_path.unlink()
        if space_dir.exists():
            shutil.rmtree(space_dir, ignore_errors=True)
        if Path("data").exists() and not any(Path("data").iterdir()):
            Path("data").rmdir()


def test_upload_document_error(client):
    """Test upload document handles errors."""
    test_client, mock_chain = client
    
    with patch('src.api.main.DocumentLoader') as mock_loader_class:
        mock_loader = Mock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load_documents.side_effect = Exception("Load error")
        
        files = {'file': ('test.txt', b'content', 'text/plain')}
        response = test_client.post("/api/spaces/test-space/documents", files=files)
    
    assert response.status_code == 500


def test_delete_space_success(client):
    """Test deleting a space."""
    test_client, mock_chain = client
    
    space_dir = Path("data") / "test-space"
    space_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with patch('src.api.main.rag_chain.vector_store.delete_collection') as mock_del:
            response = test_client.delete("/spaces/test-space")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            mock_del.assert_called_once_with("test-space")
    finally:
        if space_dir.exists():
            shutil.rmtree(space_dir, ignore_errors=True)


def test_delete_space_default_protected(client):
    """Test that default space cannot be deleted."""
    test_client, mock_chain = client
    response = test_client.delete("/spaces/default")
    assert response.status_code == 400
    data = response.json()
    assert "Cannot delete the default space" in data["detail"]


def test_delete_space_error(client):
    """Test delete space handles errors."""
    test_client, mock_chain = client
    mock_chain.vector_store.delete_collection.side_effect = Exception("Delete failed")
    response = test_client.delete("/spaces/test-space")
    assert response.status_code == 500


def test_query_request_validation(client):
    """Test QueryRequest model validation."""
    test_client, _ = client
    # Missing required field
    response = test_client.post("/spaces/test/query", json={"query": "test"})
    assert response.status_code == 422  # Validation error


def test_space_request_validation(client):
    """Test SpaceRequest model validation."""
    test_client, _ = client
    # Invalid payload
    response = test_client.post("/spaces", json={"name": "test"})
    assert response.status_code == 422  # Validation error

