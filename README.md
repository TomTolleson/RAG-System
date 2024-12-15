# RAG System with Milvus and LangChain

[![CI](https://github.com/TomTolleson/RAG-System/actions/workflows/ci.yml/badge.svg)](https://github.com/TomTolleson/RAG-System/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/TomTolleson/RAG-System/branch/main/graph/badge.svg)](https://codecov.io/gh/TomTolleson/RAG-System)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

![OpenAI](https://a11ybadges.com/badge?logo=openai) 
[![License: MIT](https://cdn.prod.website-files.com/5e0f1144930a8bc8aace526c/65dd9eb5aaca434fac4f1c34_License-MIT-blue.svg)](/LICENSE)

A Retrieval-Augmented Generation (RAG) system that combines Milvus vector database with LangChain and OpenAI for intelligent document querying and response generation.

## System Overview

This system implements RAG architecture to provide accurate, context-aware responses to questions by:
1. Storing document embeddings in Milvus vector database
2. Retrieving relevant context when queried
3. Generating human-like responses using OpenAI's language models

### Components

#### Vector Store (src/vector_store/milvus_store.py)
- Uses Milvus for efficient vector similarity search
- Stores document embeddings using OpenAI's embedding model
- Handles document addition and retrieval operations
- Configurable connection settings for Milvus database

#### RAG Chain (src/rag/rag_chain.py)
- Implements the core RAG logic
- Integrates OpenAI's ChatGPT for response generation
- Manages the retrieval-generation pipeline
- Configurable temperature and other LLM parameters

#### Document Processing (main.py)
- Handles document loading and chunking
- Configurable chunk size and overlap
- Supports text documents (expandable to other formats)

## Prerequisites

- Python 3.12+
- Docker and Docker Compose
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd RAG-System
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env
```

5. Start Milvus services:
```bash
docker-compose up -d
```

## Usage

1. Add your documents to the data directory:
```bash
mkdir data
echo "Your document content here" > data/test_document.txt
```

2. Run the system:
```bash
python main.py
```

## Configuration

### Milvus Settings
- Host: localhost (default)
- Port: 19530 (default)
- Configurable in src/config/settings.py

### Document Processing
- Chunk size: 1000 (default)
- Chunk overlap: 0 (default)
- Configurable in src/config/settings.py

### LLM Settings
- Model: OpenAI ChatGPT
- Temperature: 0.2 (default)
- Configurable in src/config/settings.py

## Use Cases

This RAG system is ideal for:
- Document question-answering
- Knowledge base augmentation
- Contextual information retrieval
- Research assistance
- Technical documentation queries

## Docker Services

The system uses several Docker containers:
- Milvus standalone server
- Etcd for metadata storage
- MinIO for object storage

Access MinIO console:
- URL: http://localhost:9015
- Credentials: minioadmin/minioadmin

## Extending the System

The system can be extended with:
- Additional document types (PDF, HTML, etc.)
- Custom embedding models
- Alternative vector databases
- Web interface
- Batch processing
- Caching mechanisms

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

[Your license information here]

## References

- [Milvus Documentation](https://milvus.io/docs)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI API Documentation](https://platform.openai.com/docs/introduction)