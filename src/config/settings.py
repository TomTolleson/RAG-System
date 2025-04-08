from pathlib import Path
import os

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ChromaDB settings
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
COLLECTION_NAME = "documents"

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Document processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 0
RETRIEVAL_K = 3

# LLM settings
TEMPERATURE = 0.2
