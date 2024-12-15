from langchain_openai import OpenAIEmbeddings

from src.config.settings import OPENAI_API_KEY


class EmbeddingHandler:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY
        )

    def get_embeddings(self):
        return self.embeddings
