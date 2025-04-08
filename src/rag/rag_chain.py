from typing import Optional, Dict, Any, List
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from ..vector_store.chroma_store import ChromaStore
import os
from dotenv import load_dotenv

load_dotenv()

class RAGChain:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Initialize ChromaStore with environment variables
        self.vector_store = ChromaStore(
            host=os.getenv("CHROMA_HOST", "localhost"),
            port=int(os.getenv("CHROMA_PORT", "8001")),
            collection_name="default",
            persist_directory="./chroma_db"
        )
        
        self.llm = ChatOpenAI(
            temperature=0.0,
            openai_api_key=openai_api_key
        )
        self.qa_chain: Optional[RetrievalQA] = None

    def initialize_chain(self, collection_name: str) -> None:
        """Initialize the QA chain for a specific collection."""
        try:
            # Create a Chroma vectorstore using the existing collection
            vectorstore = Chroma(
                client=self.vector_store._chroma_client,
                collection_name=collection_name,
                embedding_function=self.vector_store._embedding_function
            )
            
            # Create a retriever from the vectorstore
            retriever = vectorstore.as_retriever()
            
            # Initialize the QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize chain: {str(e)}")

    def query(self, query: str, space_name: str, k: int = 4) -> List[Dict[str, Any]]:
        """Query the vector store for similar documents and generate a response."""
        try:
            # Initialize the chain if not already initialized
            if not self.qa_chain:
                self.initialize_chain(space_name)
            
            # Generate response using the QA chain
            response = self.qa_chain.invoke({"query": query})
            
            # Format the response
            return [{
                "text": response["result"],
                "metadata": {"source": "qa_chain"}
            }]
        except Exception as e:
            raise Exception(f"Failed to query: {str(e)}")

    def get_spaces(self) -> List[str]:
        """Get list of existing spaces (collections)."""
        return self.vector_store.get_existing_collections()

    def add_documents(self, documents: List[Dict[str, Any]], space_name: str) -> None:
        """Add documents to the vector store."""
        self.vector_store.add_documents(documents, space_name)
