from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import logging
from ..rag.rag_chain import RAGChain
from ..rag.document_loader import DocumentLoader
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAGChain
rag_chain = RAGChain()

class QueryRequest(BaseModel):
    query: str
    space_name: str

class SpaceRequest(BaseModel):
    name: str
    documents: List[Dict[str, Any]]

class Document(BaseModel):
    text: str
    metadata: Dict[str, Any] = {}

@app.get("/api/health")
async def health_check():
    """Check if the backend is healthy"""
    try:
        # Get list of collections to verify connection
        collections = rag_chain.get_spaces()
        return {
            "status": "healthy",
            "collections": collections
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/spaces")
async def list_spaces():
    try:
        spaces = rag_chain.get_spaces()
        return {"spaces": spaces}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/spaces")
async def create_space(request: SpaceRequest):
    try:
        # Convert documents to the expected format
        documents = [{"text": doc["text"], "metadata": doc.get("metadata", {})} for doc in request.documents]
        rag_chain.add_documents(documents, request.name)
        # Initialize the chain for the new space
        rag_chain.initialize_chain(request.name)
        return {"message": f"Space '{request.name}' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/spaces/{space_name}/query")
async def query_space(space_name: str, request: QueryRequest):
    try:
        results = rag_chain.query(request.query, space_name)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/spaces/{space_name}/documents")
async def upload_document(space_name: str, file: UploadFile = File(...)):
    """Upload a document to a specific space"""
    try:
        # Create space directory if it doesn't exist
        space_dir = os.path.join("data", space_name)
        os.makedirs(space_dir, exist_ok=True)

        # Save the uploaded file
        file_path = os.path.join(space_dir, file.filename or "")
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process the document
        loader = DocumentLoader()
        documents = loader.load_documents(file_path)

        # Convert Langchain Document objects to the expected format
        processed_documents = [
            {
                "text": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in documents
        ]

        # Add to vector store
        rag_chain.add_documents(processed_documents, space_name)

        return {"message": f"Document '{file.filename}' uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/spaces/{space_name}")
async def delete_space(space_name: str):
    """Delete a space and its associated documents."""
    if space_name == "default":
        raise HTTPException(status_code=400, detail="Cannot delete the default space")
    
    try:
        # Delete the space directory if it exists
        space_dir = os.path.join("data", space_name)
        if os.path.exists(space_dir):
            import shutil
            shutil.rmtree(space_dir)
        
        # Delete the collection from ChromaDB
        rag_chain.vector_store.delete_collection(space_name)
        
        return {"message": f"Space '{space_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)  # nosec B104 