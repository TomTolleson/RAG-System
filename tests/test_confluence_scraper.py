import pytest
from unittest.mock import Mock, patch
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
def confluence_scraper(temp_dir):
    """Create a ConfluenceScraper instance for testing."""
    from src.scraper.confluence_scraper import ConfluenceScraper
    return ConfluenceScraper(
        base_url="https://example.atlassian.net/wiki",
        email="test@example.com",
        api_token="test-token",
        output_dir=str(temp_dir)
    )


def test_confluence_scraper_initialization(confluence_scraper):
    """Test ConfluenceScraper initializes correctly."""
    assert confluence_scraper.base_url == "https://example.atlassian.net/wiki"
    assert confluence_scraper.email == "test@example.com"
    assert confluence_scraper.api_token == "test-token"
    assert confluence_scraper.output_dir.exists()
    assert confluence_scraper.auth == ("test@example.com", "test-token")


def test_confluence_scraper_base_url_stripping():
    """Test ConfluenceScraper strips trailing slash from base_url."""
    from src.scraper.confluence_scraper import ConfluenceScraper
    scraper = ConfluenceScraper(
        base_url="https://example.atlassian.net/wiki/",
        email="test@example.com",
        api_token="test-token"
    )
    assert scraper.base_url == "https://example.atlassian.net/wiki"


@patch('src.scraper.confluence_scraper.requests.get')
def test_get_space_content_single_page(mock_get, confluence_scraper):
    """Test get_space_content retrieves content from a single page."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {
        'results': [{'id': '1', 'title': 'Page 1'}],
        'size': 50  # Less than limit, so only one call
    }
    mock_get.return_value = mock_response
    
    content = confluence_scraper.get_space_content("TEST")
    assert len(content) == 1
    assert content[0]['id'] == '1'


@patch('src.scraper.confluence_scraper.requests.get')
def test_get_space_content_multiple_pages(mock_get, confluence_scraper):
    """Test get_space_content handles pagination."""
    mock_response1 = Mock()
    mock_response1.raise_for_status = Mock()
    mock_response1.json.return_value = {
        'results': [{'id': str(i), 'title': f'Page {i}'} for i in range(100)],
        'size': 100  # Full page
    }
    
    mock_response2 = Mock()
    mock_response2.raise_for_status = Mock()
    mock_response2.json.return_value = {
        'results': [{'id': '100', 'title': 'Page 100'}],
        'size': 50  # Less than limit, stops here
    }
    
    mock_get.side_effect = [mock_response1, mock_response2]
    
    content = confluence_scraper.get_space_content("TEST")
    assert len(content) == 101


@patch('src.scraper.confluence_scraper.requests.get')
def test_download_attachment_success(mock_get, confluence_scraper, temp_dir):
    """Test download_attachment successfully downloads an attachment."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.iter_content.return_value = [b'attachment content']
    mock_get.return_value = mock_response
    
    attachment = {
        '_links': {'download': 'https://example.atlassian.net/wiki/attachments/test.pdf'},
        'title': 'test.pdf'
    }
    
    file_path = confluence_scraper.download_attachment(attachment)
    assert file_path is not None
    assert file_path.exists()
    assert file_path.read_bytes() == b'attachment content'


@patch('src.scraper.confluence_scraper.requests.get')
def test_download_attachment_error_handling(mock_get, confluence_scraper):
    """Test download_attachment handles errors gracefully."""
    mock_get.side_effect = Exception("Network error")
    
    attachment = {
        '_links': {'download': 'https://example.atlassian.net/wiki/attachments/test.pdf'},
        'title': 'test.pdf'
    }
    
    file_path = confluence_scraper.download_attachment(attachment)
    assert file_path is None


@patch('src.scraper.confluence_scraper.requests.get')
def test_get_page_attachments_success(mock_get, confluence_scraper):
    """Test get_page_attachments retrieves attachments for a page."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {
        'results': [
            {'id': '1', 'title': 'attachment1.pdf'},
            {'id': '2', 'title': 'attachment2.docx'}
        ]
    }
    mock_get.return_value = mock_response
    
    attachments = confluence_scraper.get_page_attachments("12345")
    assert len(attachments) == 2
    assert attachments[0]['title'] == 'attachment1.pdf'


@patch('src.scraper.confluence_scraper.requests.get')
def test_get_page_attachments_empty(mock_get, confluence_scraper):
    """Test get_page_attachments returns empty list when no attachments."""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {'results': []}
    mock_get.return_value = mock_response
    
    attachments = confluence_scraper.get_page_attachments("12345")
    assert attachments == []


def test_save_page_content_success(confluence_scraper, temp_dir):
    """Test save_page_content successfully saves page content."""
    page = {
        'title': 'Test Page',
        'body': {
            'storage': {
                'value': '<html><body>Test content</body></html>'
            }
        }
    }
    
    file_path = confluence_scraper.save_page_content(page)
    assert file_path is not None
    assert file_path.exists()
    assert 'Test_Page' in str(file_path)
    assert file_path.suffix == '.html'
    assert file_path.read_text() == '<html><body>Test content</body></html>'


def test_save_page_content_special_characters(confluence_scraper):
    """Test save_page_content handles special characters in title."""
    page = {
        'title': 'Test/Page Name',
        'body': {
            'storage': {
                'value': '<html>Content</html>'
            }
        }
    }
    
    file_path = confluence_scraper.save_page_content(page)
    assert file_path is not None
    # Check that filename has / replaced with _
    assert '/' not in file_path.name  # Should replace / with _ in filename


def test_save_page_content_error_handling(confluence_scraper):
    """Test save_page_content handles errors gracefully."""
    # Missing required fields
    page = {'title': 'Test'}
    file_path = confluence_scraper.save_page_content(page)
    assert file_path is None


@patch('src.scraper.confluence_scraper.ConfluenceScraper.get_space_content')
@patch('src.scraper.confluence_scraper.ConfluenceScraper.save_page_content')
@patch('src.scraper.confluence_scraper.ConfluenceScraper.get_page_attachments')
@patch('src.scraper.confluence_scraper.ConfluenceScraper.download_attachment')
def test_scrape_space_success(mock_download, mock_attachments, mock_save, mock_content, confluence_scraper):
    """Test scrape_space successfully scrapes a Confluence space."""
    # Mock space content
    mock_content.return_value = [
        {
            'id': '123',
            'type': 'page',
            'title': 'Test Page'
        }
    ]
    
    # Mock saving page
    mock_file = Path("test.html")
    mock_file.touch()
    mock_save.return_value = mock_file
    
    # Mock attachments
    mock_attachments.return_value = [
        {'id': '1', 'title': 'file.pdf'}
    ]
    
    # Mock downloading attachment
    mock_attach_file = Path("file.pdf")
    mock_attach_file.touch()
    mock_download.return_value = mock_attach_file
    
    files = confluence_scraper.scrape_space("TEST")
    assert len(files) == 2  # One page + one attachment
    mock_content.assert_called_once_with("TEST")


@patch('src.scraper.confluence_scraper.ConfluenceScraper.get_space_content')
def test_scrape_space_error_handling(mock_content, confluence_scraper):
    """Test scrape_space handles errors gracefully."""
    mock_content.side_effect = Exception("API Error")
    files = confluence_scraper.scrape_space("TEST")
    assert isinstance(files, list)


@patch('src.scraper.confluence_scraper.ConfluenceScraper.get_space_content')
def test_scrape_space_non_page_content(mock_content, confluence_scraper):
    """Test scrape_space skips non-page content."""
    mock_content.return_value = [
        {
            'id': '123',
            'type': 'comment',  # Not a page
            'title': 'Comment'
        }
    ]
    
    files = confluence_scraper.scrape_space("TEST")
    assert len(files) == 0  # No pages, so no files

