from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Milvus settings
MILVUS_HOST = "localhost"
MILVUS_PORT = 19530
COLLECTION_NAME = "documents"

# OpenAI settings
OPENAI_API_KEY = "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"

# Document processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 0
RETRIEVAL_K = 3

# LLM settings
TEMPERATURE = 0.2
