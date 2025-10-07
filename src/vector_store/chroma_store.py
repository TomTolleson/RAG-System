import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from src.embeddings.openai_embeddings import OpenAIEmbeddings

load_dotenv()


class ChromaStore:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "default",
        embedding_function: Optional[Any] = None,
        persist_directory: Optional[str] = None,
        ssl: bool = False,
        headers: Optional[Dict[str, str]] = None,
        tenant: str = "default_tenant",
        database: str = "default_database"
    ):
        self._host = host
        self._port = port
        self._collection_name = collection_name
        self._embedding_function = embedding_function or OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        self._persist_directory = persist_directory or os.path.join(os.getcwd(), "chroma_db")
        self._ssl = ssl
        self._headers = headers
        self._tenant = tenant
        self._database = database
        
        # Initialize the ChromaDB client
        self._chroma_client = chromadb.PersistentClient(
            path=self._persist_directory,
            settings=Settings(
                chroma_server_host=host,
                chroma_server_http_port=port,
                chroma_server_ssl_enabled=ssl
            )
        )
        
        # Get or create the collection
        self._collection = self._get_or_create_collection()

    def _get_or_create_collection(self) -> Any:
        """Get or create a collection with the specified name."""
        try:
            return self._chroma_client.get_or_create_collection(
                name=self._collection_name,
                embedding_function=self._embedding_function
            )
        except Exception as e:
            raise Exception(f"Failed to get or create collection: {str(e)}")

    def add_documents(self, documents: List[Dict[str, Any]], collection_name: str) -> None:
        """Add documents to ChromaDB collection."""
        try:
            # Get or create collection
            collection = self._chroma_client.get_or_create_collection(collection_name)

            # Prepare data
            texts: List[str] = []
            metadata: List[Dict[str, Any]] = []

            for doc in documents:
                # Support LangChain Document objects and plain dicts
                if hasattr(doc, "page_content"):
                    texts.append(str(getattr(doc, "page_content")))
                    meta = getattr(doc, "metadata", {}) or {}
                    metadata.append(meta)
                elif isinstance(doc, dict):
                    texts.append(str(doc.get("text", "")))
                    metadata.append(doc.get("metadata", {}) or {})
                else:
                    texts.append(str(doc))
                    metadata.append({})

            embeddings = self._embedding_function.embed_documents(texts)
            # Generate IDs (ChromaDB requires string IDs)
            ids = [str(i) for i in range(len(texts))]

            # Add documents
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadata,
                ids=ids
            )

        except Exception as e:
            raise Exception(f"Failed to add documents to ChromaDB: {str(e)}")

    def similarity_search(self, query: str, collection_name: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for similar documents in ChromaDB collection."""
        try:
            # Get collection
            try:
                collection = self._chroma_client.get_collection(collection_name)
            except ValueError:
                # Collection doesn't exist
                return []

            # Generate query embedding
            query_embedding = self._embedding_function.embed_query(query)

            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )

            # Format results
            documents = []
            for i in range(len(results["documents"][0])):
                documents.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1.0 - float(results["distances"][0][i])  # Convert distance to similarity score
                })

            return documents

        except Exception as e:
            raise Exception(f"Failed to search in ChromaDB: {str(e)}")

    def get_existing_collections(self) -> List[str]:
        """Get list of existing collections."""
        try:
            return [col.name for col in self._chroma_client.list_collections()]
        except Exception as e:
            raise Exception(f"Failed to get collections from ChromaDB: {str(e)}")

    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection from ChromaDB."""
        try:
            self._chroma_client.delete_collection(collection_name)
        except Exception as e:
            raise Exception(f"Failed to delete collection from ChromaDB: {str(e)}")

    def __del__(self):
        """Clean up resources when the object is destroyed."""
        # ChromaDB handles cleanup automatically
