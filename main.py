from pathlib import Path

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader

from src.config.settings import CHUNK_SIZE, CHUNK_OVERLAP
from src.rag.rag_chain import RAGChain

def load_documents(file_path):
    loader = TextLoader(file_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return text_splitter.split_documents(documents)

def main():
    # Initialize RAG chain
    rag_chain = RAGChain()
    
    # Initialize vector store and add documents
    data_path = Path("data/test_document.txt")
    if not data_path.exists():
        raise FileNotFoundError(f"Document not found at {data_path}")
    
    documents = load_documents(data_path)
    rag_chain.vector_store.add_documents(documents)
    
    # Query the system
    question = "What are the key features of Milvus?"
    result = rag_chain.query(question)
    print(result)

if __name__ == "__main__":
    main()
