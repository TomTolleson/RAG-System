import argparse
from src.scraper.web_scraper import WebScraper

def main():
    parser = argparse.ArgumentParser(description="Web Scraper for Document Collection")
    parser.add_argument("url", help="Base URL to start scraping from")
    parser.add_argument("--depth", type=int, default=2, help="Maximum depth to crawl (default: 2)")
    parser.add_argument("--output", default="data", help="Output directory for downloaded files (default: data)")
    
    args = parser.parse_args()
    
    try:
        scraper = WebScraper(args.url, args.output)
        downloaded_files = scraper.start_scraping(args.depth)
        
        print(f"\nScraping completed!")
        print(f"Total files downloaded: {len(downloaded_files)}")
        print("\nDownloaded files:")
        for file in downloaded_files:
            print(f"- {file}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 