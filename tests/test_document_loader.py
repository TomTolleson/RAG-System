from pathlib import Path
import pytest


def test_load_txt_splits_chunks(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Line1\nLine2\nLine3\n")

    from src.rag.document_loader import DocumentLoader

    loader = DocumentLoader()
    docs = loader.load_documents(file_path)
    assert len(docs) >= 1
    assert all(hasattr(d, 'page_content') for d in docs)


def test_load_directory_filters_and_processes(tmp_path: Path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.md").write_text("# title")
    (tmp_path / "c.unsupported").write_text("x")

    from src.rag.document_loader import DocumentLoader

    loader = DocumentLoader()
    docs = loader.load_directory(tmp_path)
    # at least processed supported files
    assert len(docs) >= 1


def test_process_table_data_handles_lines(mocker):
    from src.rag.document_loader import DocumentLoader

    dl = DocumentLoader()
    content = "File Name Format\nAnnexCloud CSV SFTP SFTP/path Incremental AnnexCloud\n"
    docs = dl._process_table_data(content)
    assert len(docs) >= 1
    assert docs[0].metadata.get("is_structured") is True


def test_clean_table_text():
    """Test _clean_table_text method normalizes text correctly."""
    from src.rag.document_loader import DocumentLoader
    
    loader = DocumentLoader()
    text = "  multiple    spaces   here  "
    cleaned = loader._clean_table_text(text)
    assert cleaned == "multiple spaces here"


def test_clean_table_text_ocr_fixes():
    """Test _clean_table_text fixes OCR issues."""
    from src.rag.document_loader import DocumentLoader
    
    loader = DocumentLoader()
    text = "word.word another_word"
    cleaned = loader._clean_table_text(text)
    assert "word word" in cleaned


def test_extract_table_fields():
    """Test _extract_table_fields extracts structured data."""
    from src.rag.document_loader import DocumentLoader
    
    loader = DocumentLoader()
    line = "AnnexCloud CSV SFTP SFTP/path Incremental"
    fields = loader._extract_table_fields(line)
    assert isinstance(fields, dict)


def test_extract_table_fields_empty():
    """Test _extract_table_fields with no matches."""
    from src.rag.document_loader import DocumentLoader
    
    loader = DocumentLoader()
    line = "Random text with no structure"
    fields = loader._extract_table_fields(line)
    assert isinstance(fields, dict)


def test_load_directory_not_directory():
    """Test load_directory raises error for non-directory."""
    from src.rag.document_loader import DocumentLoader
    
    loader = DocumentLoader()
    with pytest.raises(ValueError):
        loader.load_directory("/nonexistent/path/file.txt")


def test_get_loader_unsupported_type():
    """Test _get_loader raises error for unsupported file types."""
    from src.rag.document_loader import DocumentLoader
    
    loader = DocumentLoader()
    with pytest.raises(ValueError):
        loader._get_loader("test.xyz")


def test_get_loader_supported_types(tmp_path: Path):
    """Test _get_loader returns correct loader for supported types."""
    from src.rag.document_loader import DocumentLoader
    
    loader = DocumentLoader()
    
    # Test various supported file types
    test_files = {
        ".txt": "sample.txt",
        ".pdf": "sample.pdf",
        ".docx": "sample.docx",
        ".md": "sample.md",
        ".html": "sample.html",
        ".csv": "sample.csv"
    }
    
    for ext, filename in test_files.items():
        file_path = tmp_path / filename
        file_path.touch()
        loader_instance = loader._get_loader(file_path)
        assert loader_instance is not None


def test_process_table_data_error_handling():
    """Test _process_table_data handles errors gracefully."""
    from src.rag.document_loader import DocumentLoader
    from unittest.mock import patch
    
    loader = DocumentLoader()
    
    # Mock an error condition
    with patch.object(loader, '_extract_table_fields', side_effect=Exception("Error")):
        content = "Table data here"
        docs = loader._process_table_data(content)
        # Should fall back to basic text processing
        assert len(docs) >= 1
        assert docs[0].metadata.get("is_structured") is False


def test_load_documents_error_handling(tmp_path: Path):
    """Test load_documents handles errors appropriately."""
    from src.rag.document_loader import DocumentLoader
    
    loader = DocumentLoader()
    
    # Create a file but make it unreadable or corrupted
    with pytest.raises(Exception):  # Should raise RuntimeError
        # Try to load a non-existent file
        loader.load_documents(tmp_path / "nonexistent.txt")


def test_load_documents_structured_preservation(tmp_path: Path):
    """Test that structured documents preserve metadata."""
    from src.rag.document_loader import DocumentLoader
    
    loader = DocumentLoader()
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("col1,col2\nval1,val2\n")
    
    docs = loader.load_documents(csv_file)
    assert len(docs) >= 1
    # CSV should be marked as structured
    assert any(d.metadata.get("is_structured", False) for d in docs)


def test_load_directory_empty_directory(tmp_path: Path):
    """Test load_directory with empty directory."""
    from src.rag.document_loader import DocumentLoader
    
    loader = DocumentLoader()
    docs = loader.load_directory(tmp_path)
    assert isinstance(docs, list)
    assert len(docs) == 0

