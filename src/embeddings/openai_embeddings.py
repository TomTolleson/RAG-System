from typing import List, Union
from openai import OpenAI


class OpenAIEmbeddings:
    def __init__(self, api_key: str, model_name: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def __call__(self, input: Union[str, List[str]]) -> List[List[float]]:
        """Generate embeddings for input text(s)."""
        try:
            if isinstance(input, str):
                input = [input]
            input = [str(text) for text in input]
            
            response = self.client.embeddings.create(
                model=self.model_name,
                input=input
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise Exception(f"Failed to generate embeddings: {str(e)}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        try:
            texts = [str(text) for text in texts]

            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise Exception(f"Failed to generate embeddings: {str(e)}")

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single text query."""
        try:
            text = str(text)

            response = self.client.embeddings.create(
                model=self.model_name,
                input=[text]
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to generate query embedding: {str(e)}")
