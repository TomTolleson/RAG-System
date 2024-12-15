from typing import List, Optional
from langchain_community.vectorstores import Milvus
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
import os
from pydantic import SecretStr

# Load environment variables
load_dotenv()

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")

class MilvusStore:
    def __init__(self) -> None:
        api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        secret_key: Optional[SecretStr] = SecretStr(api_key) if api_key else None
        self.embeddings = OpenAIEmbeddings(api_key=secret_key)
        self.vector_store: Optional[Milvus] = None

    def add_documents(self, documents: List[Document]) -> Milvus:
        self.vector_store = Milvus.from_documents(
            documents,
            self.embeddings,
            connection_args={"host": MILVUS_HOST, "port": MILVUS_PORT}
        )
        return self.vector_store

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        if self.vector_store is None:
            raise ValueError("No documents have been added to the vector store")
        return self.vector_store.similarity_search(query, k=k)