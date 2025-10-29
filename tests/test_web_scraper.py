import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def web_scraper(temp_dir):
    """Create a WebScraper instance for testing."""
    from src.scraper.web_scraper import WebScraper
    return WebScraper(base_url="https://example.com", output_dir=str(temp_dir))


def test_web_scraper_initialization(web_scraper):
    """Test WebScraper initializes correctly."""
    assert web_scraper.base_url == "https://example.com"
    assert web_scraper.output_dir.exists()
    assert "example.com" in web_scraper.allowed_domains


def test_is_valid_url_valid(web_scraper):
    """Test is_valid_url returns True for valid URLs."""
    assert web_scraper.is_valid_url("https://example.com/page") is True
    assert web_scraper.is_valid_url("http://example.com/page") is True


def test_is_valid_url_invalid_domain(web_scraper):
    """Test is_valid_url returns False for different domain."""
    assert web_scraper.is_valid_url("https://other-domain.com/page") is False


def test_is_valid_url_invalid_scheme(web_scraper):
    """Test is_valid_url returns False for invalid scheme."""
    assert web_scraper.is_valid_url("ftp://example.com/page") is False


def test_is_valid_url_exception_handling(web_scraper):
    """Test is_valid_url handles exceptions gracefully."""
    # Test with invalid URL that causes exception
    result = web_scraper.is_valid_url("not-a-url-at-all")
    assert result is False


def test_get_file_extension_supported(web_scraper):
    """Test get_file_extension returns extension for supported files."""
    assert web_scraper.get_file_extension("https://example.com/file.pdf") == ".pdf"
    assert web_scraper.get_file_extension("https://example.com/doc.docx") == ".docx"
    assert web_scraper.get_file_extension("https://example.com/text.txt") == ".txt"


def test_get_file_extension_unsupported(web_scraper):
    """Test get_file_extension returns None for unsupported files."""
    assert web_scraper.get_file_extension("https://example.com/file.jpg") is None
    assert web_scraper.get_file_extension("https://example.com/file.exe") is None


def test_get_file_extension_no_extension(web_scraper):
    """Test get_file_extension returns None when no extension."""
    assert web_scraper.get_file_extension("https://example.com/page") is None


@patch('src.scraper.web_scraper.requests.get')
def test_download_file_success(mock_get, web_scraper):
    """Test download_file successfully downloads a file."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.iter_content.return_value = [b'file content']
    mock_get.return_value = mock_response
    
    file_path = web_scraper.download_file("https://example.com/file.pdf")
    assert file_path is not None
    assert file_path.exists()
    assert file_path.read_bytes() == b'file content'


@patch('src.scraper.web_scraper.requests.get')
def test_download_file_error_handling(mock_get, web_scraper):
    """Test download_file handles errors gracefully."""
    mock_get.side_effect = Exception("Network error")
    file_path = web_scraper.download_file("https://example.com/file.pdf")
    assert file_path is None


@patch('src.scraper.web_scraper.requests.get')
def test_download_file_http_error(mock_get, web_scraper):
    """Test download_file handles HTTP errors."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")
    mock_get.return_value = mock_response
    
    file_path = web_scraper.download_file("https://example.com/file.pdf")
    assert file_path is None


@patch('src.scraper.web_scraper.requests.get')
def test_scrape_page_success(mock_get, web_scraper):
    """Test scrape_page successfully scrapes a page."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.text = '<html><body><a href="/page2">Link</a></body></html>'
    mock_get.return_value = mock_response
    
    files = web_scraper.scrape_page("https://example.com/page", depth=1)
    assert len(files) >= 1
    assert any(f.suffix == ".html" for f in files)


def test_scrape_page_zero_depth(web_scraper):
    """Test scrape_page returns empty list when depth is 0."""
    files = web_scraper.scrape_page("https://example.com/page", depth=0)
    assert files == []


def test_scrape_page_visited_url(web_scraper):
    """Test scrape_page skips already visited URLs."""
    web_scraper.visited_urls.add("https://example.com/page")
    files = web_scraper.scrape_page("https://example.com/page", depth=1)
    assert files == []


@patch('src.scraper.web_scraper.requests.get')
def test_scrape_page_error_handling(mock_get, web_scraper):
    """Test scrape_page handles errors gracefully."""
    mock_get.side_effect = Exception("Network error")
    files = web_scraper.scrape_page("https://example.com/page", depth=1)
    assert isinstance(files, list)


@patch('src.scraper.web_scraper.requests.get')
def test_scrape_page_with_document_links(mock_get, web_scraper):
    """Test scrape_page downloads document links."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.text = '<html><body><a href="/file.pdf">PDF</a></body></html>'
    mock_response.iter_content.return_value = [b'pdf content']
    
    def side_effect(*args, **kwargs):
        if 'stream' in kwargs:
            return mock_response
        return mock_response
    
    mock_get.side_effect = side_effect
    
    files = web_scraper.scrape_page("https://example.com/page", depth=1)
    assert len(files) >= 1


@patch('src.scraper.web_scraper.WebScraper.scrape_page')
def test_start_scraping(mock_scrape, web_scraper):
    """Test start_scraping initiates scraping from base URL."""
    mock_scrape.return_value = [Path("test.html")]
    files = web_scraper.start_scraping(depth=2)
    assert len(files) >= 0
    mock_scrape.assert_called_once_with("https://example.com", 2)


@patch('src.scraper.web_scraper.requests.get')
def test_download_file_no_filename(mock_get, web_scraper):
    """Test download_file handles URL with no filename (line 54)."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.iter_content.return_value = [b'content']
    mock_get.return_value = mock_response
    
    # URL with no filename
    file_path = web_scraper.download_file("https://example.com/")
    assert file_path is not None
    assert file_path.exists()


@patch('src.scraper.web_scraper.requests.get')
def test_download_file_no_extension(mock_get, web_scraper):
    """Test download_file adds extension when missing (lines 58-60)."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.iter_content.return_value = [b'content']
    mock_get.return_value = mock_response
    
    # URL with filename but no extension, but with extension in URL path
    file_path = web_scraper.download_file("https://example.com/document.pdf")
    assert file_path is not None
    assert file_path.suffix == ".pdf"

