import argparse
from src.scraper.confluence_scraper import ConfluenceScraper
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Confluence Wiki Scraper")
    parser.add_argument("url", help="Base URL of the Confluence instance")
    parser.add_argument("space_key", help="Space key to scrape")
    parser.add_argument("--email", help="Email for authentication (or set CONFLUENCE_EMAIL env var)")
    parser.add_argument("--api-token", help="API token for authentication (or set CONFLUENCE_API_TOKEN env var)")
    parser.add_argument("--output", default="data", help="Output directory for downloaded files")
    
    args = parser.parse_args()
    
    # Get credentials from args or environment variables
    email = args.email or os.getenv('CONFLUENCE_EMAIL')
    api_token = args.api_token or os.getenv('CONFLUENCE_API_TOKEN')
    
    if not email or not api_token:
        print("Error: Email and API token are required.")
        print("You can provide them via command line arguments or environment variables:")
        print("  --email and --api-token")
        print("  CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN")
        return
    
    try:
        scraper = ConfluenceScraper(
            base_url=args.url,
            email=email,
            api_token=api_token,
            output_dir=args.output
        )
        
        print(f"Starting to scrape Confluence space: {args.space_key}")
        downloaded_files = scraper.scrape_space(args.space_key)
        
        print(f"\nScraping completed!")
        print(f"Total files downloaded: {len(downloaded_files)}")
        print("\nDownloaded files:")
        for file in downloaded_files:
            print(f"- {file}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 