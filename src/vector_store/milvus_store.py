from typing import List, Optional
from langchain_community.vectorstores import Milvus
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
import os
from pymilvus import connections, utility

# Load environment variables
load_dotenv()

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")

class MilvusStore:
    def __init__(self, space_name: str = "default") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.embeddings = OpenAIEmbeddings(api_key=api_key)
        self.vector_store: Optional[Milvus] = None
        self.space_name = space_name
        self.collection_name = f"rag_documents_{space_name}"

    def add_documents(self, documents: List[Document]) -> Milvus:
        alias = "default"
        try:
            connections.connect(host=MILVUS_HOST, port=MILVUS_PORT, alias=alias)
            self.vector_store = Milvus.from_documents(
                documents,
                self.embeddings,
                connection_args={"host": MILVUS_HOST, "port": MILVUS_PORT},
                collection_name=self.collection_name
            )
            return self.vector_store
        finally:
            try:
                connections.disconnect(alias)
            except:
                pass

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        if self.vector_store is None:
            raise ValueError("No documents have been added to the vector store")
        return self.vector_store.similarity_search(query, k=k)

    def get_existing_collections(self) -> List[str]:
        """Get a list of all existing collections in Milvus"""
        alias = "default"
        try:
            connections.connect(host=MILVUS_HOST, port=MILVUS_PORT, alias=alias)
            collections = utility.list_collections()
            return [col for col in collections if col.startswith("rag_documents_")]
        finally:
            try:
                connections.disconnect(alias)
            except:
                pass