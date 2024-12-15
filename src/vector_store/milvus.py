from langchain_milvus import Milvus

from src.config.settings import COLLECTION_NAME, MILVUS_HOST, MILVUS_PORT
from src.embeddings.embedding_handler import EmbeddingHandler


class MilvusStore:
    def __init__(self):
        self.embedding_handler = EmbeddingHandler()
        self.vector_store = Milvus(
            embedding_function=self.embedding_handler.get_embeddings(),
            connection_args={
                "host": MILVUS_HOST,
                "port": MILVUS_PORT
            },
            collection_name=COLLECTION_NAME
        )

    def add_documents(self, documents):
        return self.vector_store.add_documents(documents)

    def get_retriever(self, search_kwargs=None):
        if search_kwargs is None:
            search_kwargs = {"k": 3}
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)
