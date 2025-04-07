from typing import Optional, Dict, Any, List
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from ..vector_store.milvus_store import MilvusStore
import os
from dotenv import load_dotenv
from pymilvus import connections, utility

load_dotenv()

class RAGChain:
    def __init__(self, space_name: str = "default") -> None:
        self.vector_store = MilvusStore(space_name=space_name)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.llm = ChatOpenAI(
            temperature=0.0,
            api_key=api_key
        )
        self.qa_chain: Optional[RetrievalQA] = None
        self.space_name = space_name

    def initialize_chain(self) -> None:
        if self.vector_store.vector_store is None:
            raise ValueError("Vector store has not been initialized with documents")
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.vector_store.as_retriever()
        )

    def query(self, question: str) -> str:
        if self.qa_chain is None:
            self.initialize_chain()
        if self.qa_chain is None:
            raise RuntimeError("Failed to initialize QA chain")
        result = self.qa_chain.invoke({"query": question})
        return str(result.get("result", ""))

    @staticmethod
    def get_available_spaces() -> List[str]:
        """Get a list of all available spaces"""
        alias = "default"
        try:
            connections.connect(
                host=os.getenv("MILVUS_HOST", "localhost"),
                port=os.getenv("MILVUS_PORT", "19530"),
                alias=alias
            )
            collections = utility.list_collections()
            return [col.replace("rag_documents_", "") for col in collections if col.startswith("rag_documents_")]
        finally:
            try:
                connections.disconnect(alias)
            except:
                pass
