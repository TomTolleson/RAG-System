from setuptools import setup, find_packages

setup(
    name="rag-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain==0.3.27",
        "langchain-openai==0.3.35",
        "langchain-community==0.3.30",
        "fastapi==0.118.0",
        "uvicorn==0.37.0",
        "python-multipart==0.0.20",
        "openai==1.12.0",
        "chromadb==0.4.22",
        "python-dotenv==1.1.1",
        "pydantic==2.12.0",
        "unstructured==0.18.15",
        "pypdf==6.1.1",
        "python-docx==1.2.0",
        "beautifulsoup4==4.14.2",
        "lxml==6.0.2",
        "requests==2.32.5",
        "urllib3==1.26.18",
        "tqdm==4.67.1",
        "httpx==0.28.1"
    ],
) 