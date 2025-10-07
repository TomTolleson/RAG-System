from pathlib import Path
import tempfile
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

