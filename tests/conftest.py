import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_document():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document about Milvus.")
        temp_path = Path(f.name)
    yield temp_path
    temp_path.unlink()  # Cleanup after test

@pytest.fixture
def mock_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123") 