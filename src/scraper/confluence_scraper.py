import os
import requests
from pathlib import Path
import logging
from typing import List, Dict, Any
import json
from urllib.parse import urljoin
import base64

class ConfluenceScraper:
    def __init__(self, base_url: str, email: str, api_token: str, output_dir: str = "data"):
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.email = email
        self.api_token = api_token
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Set up authentication
        self.auth = (email, api_token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_space_content(self, space_key: str) -> List[Dict[str, Any]]:
        """Get all content from a Confluence space."""
        content = []
        start = 0
        limit = 100
        
        while True:
            url = f"{self.base_url}/rest/api/space/{space_key}/content"
            params = {
                'start': start,
                'limit': limit,
                'expand': 'body.storage,version,ancestors'
            }
            
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers,
                params=params,
                timeout=30  # nosec B113
            )
            response.raise_for_status()
            
            data = response.json()
            content.extend(data.get('results', []))
            
            if data.get('size', 0) < limit:
                break
                
            start += limit
            
        return content

    def download_attachment(self, attachment: Dict[str, Any]) -> Path:
        """Download a Confluence attachment."""
        try:
            download_url = attachment['_links']['download']
            filename = attachment['title']
            
            response = requests.get(
                download_url,
                auth=self.auth,
                headers=self.headers,
                stream=True,
                timeout=30  # nosec B113
            )
            response.raise_for_status()
            
            output_path = self.output_dir / filename
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.logger.info(f"Downloaded attachment: {filename}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error downloading attachment: {str(e)}")
            return None

    def get_page_attachments(self, page_id: str) -> List[Dict[str, Any]]:
        """Get all attachments for a page."""
        url = f"{self.base_url}/rest/api/content/{page_id}/child/attachment"
        response = requests.get(
            url,
            auth=self.auth,
            headers=self.headers,
            timeout=30  # nosec B113
        )
        response.raise_for_status()
        
        return response.json().get('results', [])

    def save_page_content(self, page: Dict[str, Any]) -> Path:
        """Save page content as HTML."""
        try:
            title = page['title']
            content = page['body']['storage']['value']
            
            # Create a filename-safe version of the title
            filename = f"{title.replace('/', '_').replace(' ', '_')}.html"
            output_path = self.output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Saved page: {title}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error saving page: {str(e)}")
            return None

    def scrape_space(self, space_key: str) -> List[Path]:
        """Scrape all content from a Confluence space."""
        downloaded_files = []
        
        try:
            # Get all content from the space
            content = self.get_space_content(space_key)
            
            for item in content:
                if item['type'] == 'page':
                    # Save the page content
                    page_path = self.save_page_content(item)
                    if page_path:
                        downloaded_files.append(page_path)
                    
                    # Get and download attachments
                    attachments = self.get_page_attachments(item['id'])
                    for attachment in attachments:
                        attachment_path = self.download_attachment(attachment)
                        if attachment_path:
                            downloaded_files.append(attachment_path)
                            
        except Exception as e:
            self.logger.error(f"Error scraping space: {str(e)}")
            
        return downloaded_files 