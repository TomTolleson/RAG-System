from langchain_community.vectorstores import Milvus
from langchain_openai import OpenAIEmbeddings
from ..config.settings import OPENAI_API_KEY, MILVUS_HOST, MILVUS_PORT

class MilvusStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.vector_store = None

    def add_documents(self, documents):
        self.vector_store = Milvus.from_documents(
            documents,
            self.embeddings,
            connection_args={"host": MILVUS_HOST, "port": MILVUS_PORT}
        )
        return self.vector_store

    def similarity_search(self, query, k=4):
        if self.vector_store is None:
            raise ValueError("No documents have been added to the vector store")
        return self.vector_store.similarity_search(query, k=k) 