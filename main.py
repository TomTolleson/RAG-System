import argparse
from pathlib import Path
from typing import Optional
import logging

from src.rag.document_loader import DocumentLoader
from src.rag.rag_chain import RAGChain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_documents(directory_path: Path, rag_chain: RAGChain) -> None:
    """Process all documents in the given directory."""
    try:
        document_loader = DocumentLoader()
        documents = document_loader.load_directory(directory_path)
        
        if not documents:
            logger.warning(f"No documents found in {directory_path}")
            return
            
        logger.info(f"Processing {len(documents)} document chunks...")
        rag_chain.vector_store.add_documents(documents)
        logger.info("Documents processed successfully")
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        raise

def interactive_query(rag_chain: RAGChain) -> None:
    """Run an interactive query session."""
    print("\nWelcome to the RAG System! Type 'exit' to quit.")
    print("You can ask questions about your documents, and I'll try to answer them.")
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            if question.lower() == 'exit':
                break
                
            if not question:
                continue
                
            result = rag_chain.query(question)
            print("\nAnswer:", result)
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            print("Sorry, there was an error processing your question. Please try again.")

def main() -> None:
    parser = argparse.ArgumentParser(description="RAG System for Document Question Answering")
    parser.add_argument(
        "--documents",
        type=str,
        default="data",
        help="Path to directory containing documents (default: data/)"
    )
    args = parser.parse_args()
    
    try:
        # Initialize RAG chain
        logger.info("Initializing RAG system...")
        rag_chain = RAGChain()
        
        # Process documents
        documents_path = Path(args.documents)
        if not documents_path.exists():
            logger.error(f"Documents directory not found: {documents_path}")
            return
            
        process_documents(documents_path, rag_chain)
        
        # Start interactive query session
        interactive_query(rag_chain)
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()

