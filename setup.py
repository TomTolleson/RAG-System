from setuptools import setup, find_packages

setup(
    name="rag-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain==0.1.0",
        "langchain-openai==0.0.2",
        "langchain-community==0.0.10",
        "fastapi==0.109.2",
        "uvicorn==0.27.1",
        "python-multipart==0.0.9",
        "openai==1.95.1",
        "chromadb==0.4.22",
        "python-dotenv==1.0.1",
        "pydantic==2.10.3",
        "unstructured==0.10.30",
        "pypdf==4.0.0",
        "python-docx==1.0.1",
        "beautifulsoup4==4.12.0",
        "lxml==4.9.0",
        "requests==2.31.0",
        "urllib3==1.26.18",
        "tqdm==4.66.0",
        "httpx==0.27.0"
    ],
) 