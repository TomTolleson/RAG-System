from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from ..vector_store.milvus_store import MilvusStore
from ..config.settings import OPENAI_API_KEY, TEMPERATURE

class RAGChain:
    def __init__(self):
        self.vector_store = MilvusStore()
        self.llm = ChatOpenAI(
            temperature=TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )
        self.qa_chain = None

    def initialize_chain(self):
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
        return self.qa_chain.invoke({"query": question})["result"]
