import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pathlib import Path
import logging
from typing import Set, List, Optional
import time

class WebScraper:
    def __init__(self, base_url: str, output_dir: str = "data"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.visited_urls: Set[str] = set()
        self.allowed_domains: Set[str] = {urlparse(base_url).netloc}
        self.supported_extensions = {'.pdf', '.doc', '.docx', '.txt', '.md', '.html', '.htm'}
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def is_valid_url(self, url: str) -> bool:
        """Check if the URL is valid and belongs to the allowed domains."""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ['http', 'https'] and
                parsed.netloc in self.allowed_domains
            )
        except:
            return False

    def get_file_extension(self, url: str) -> Optional[str]:
        """Extract file extension from URL if it's a document."""
        path = urlparse(url).path
        ext = os.path.splitext(path)[1].lower()
        return ext if ext in self.supported_extensions else None

    def download_file(self, url: str) -> Optional[Path]:
        """Download a file from the given URL."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get filename from URL or content-disposition
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = f"document_{int(time.time())}"
            
            # Ensure filename has an extension
            if not os.path.splitext(filename)[1]:
                ext = self.get_file_extension(url)
                if ext:
                    filename += ext
            
            output_path = self.output_dir / filename
            
            # Save the file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.logger.info(f"Downloaded: {filename}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error downloading {url}: {str(e)}")
            return None

    def scrape_page(self, url: str, depth: int = 2) -> List[Path]:
        """Scrape a web page and its links up to a certain depth."""
        if depth <= 0 or url in self.visited_urls:
            return []
            
        self.visited_urls.add(url)
        downloaded_files = []
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Save the HTML page
            filename = f"page_{len(self.visited_urls)}.html"
            output_path = self.output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            downloaded_files.append(output_path)
            
            # Parse the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                
                # Check if it's a document
                ext = self.get_file_extension(absolute_url)
                if ext:
                    file_path = self.download_file(absolute_url)
                    if file_path:
                        downloaded_files.append(file_path)
                # If it's another page, scrape it recursively
                elif self.is_valid_url(absolute_url):
                    downloaded_files.extend(self.scrape_page(absolute_url, depth - 1))
                    
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            
        return downloaded_files

    def start_scraping(self, depth: int = 2) -> List[Path]:
        """Start the scraping process from the base URL."""
        self.logger.info(f"Starting scraping from {self.base_url}")
        return self.scrape_page(self.base_url, depth) 