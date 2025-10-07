from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from typing import Optional
from pydantic import SecretStr

# Load environment variables from .env file
load_dotenv()


class EmbeddingHandler:
    def __init__(self):
        api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        secret_key: Optional[SecretStr] = SecretStr(api_key) if api_key else None
        self.embeddings = OpenAIEmbeddings(
            api_key=secret_key
        )
    
    def get_embeddings(self) -> OpenAIEmbeddings:
        return self.embeddings
