from typing import Optional, Dict, Any
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from ..vector_store.milvus_store import MilvusStore
import os
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

class RAGChain:
    def __init__(self) -> None:
        self.vector_store = MilvusStore()
        api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        secret_key: Optional[SecretStr] = SecretStr(api_key) if api_key else None
        self.llm = ChatOpenAI(
            temperature=0.0,
            api_key=secret_key
        )
        self.qa_chain: Optional[RetrievalQA] = None

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
        assert self.qa_chain is not None  # for mypy
        result = self.qa_chain.invoke({"query": question})
        return str(result.get("result", ""))
