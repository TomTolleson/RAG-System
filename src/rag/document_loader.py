from pathlib import Path
from typing import List, Union, Dict
from langchain.schema import Document
from langchain_community.document_loaders import TextLoader, CSVLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config.settings import CHUNK_SIZE, CHUNK_OVERLAP
import re


class DocumentLoader:
    """Handles loading and processing of various document types."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""],
            keep_separator=True
        )
        
    def _get_loader(self, file_path: Union[str, Path]) -> Union[
        TextLoader,
        PyPDFLoader,
        UnstructuredWordDocumentLoader,
        UnstructuredMarkdownLoader,
        UnstructuredHTMLLoader,
        CSVLoader,
    ]:
        """Returns the appropriate loader based on file extension."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            return TextLoader(str(file_path))
        elif extension == '.pdf':
            return PyPDFLoader(str(file_path))
        elif extension in ['.doc', '.docx']:
            return UnstructuredWordDocumentLoader(str(file_path), mode="elements")
        elif extension == '.md':
            return UnstructuredMarkdownLoader(str(file_path))
        elif extension in ['.html', '.htm']:
            return UnstructuredHTMLLoader(str(file_path))
        elif extension == '.csv':
            return CSVLoader(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    def _clean_table_text(self, text: str) -> str:
        """Clean and normalize table text."""
        # Remove extra spaces and normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Fix common OCR issues
        text = text.replace('_', ' ')
        text = re.sub(r'(?<=\w)\.(?=\w)', ' ', text)  # Split words joined by periods
        # Fix specific OCR issues in this dataset
        text = text.replace('exCloud', 'exCloud')
        text = text.replace('aarVoice', 'aarVoice')
        text = text.replace('merceCloud', 'merceCloud')
        text = text.replace('ketingCloud', 'ketingCloud')
        return text.strip()
    
    def _extract_table_fields(self, line: str) -> Dict[str, str]:
        """Extract structured fields from a table line."""
        # Common patterns in the data
        patterns = {
            'name': r'^([\w\-\.]+(?:\s+[\w\-\.]+)*)',
            'format': r'CSV',
            'source': r'SFTP|S3',
            'location': r'SFTP/[\w/\-]+|s3://[\w\-/]+',
            'cadence': r'15 minute sentinel|8 PM Daily|monthly drop',
            'type': r'Incremental|Snapshot',
            'system': r'AnnexCloud|BazaarVoice|CommerceCloud|MarketingCloud|GoogleAnalytics'
        }
        
        fields = {}
        text = self._clean_table_text(line)
        
        # Extract each field using patterns
        for field, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                fields[field] = match.group(0)
                # Remove matched text to avoid double-matching
                text = text.replace(match.group(0), '', 1)
        
        return fields
    
    def _process_table_data(self, content: str) -> List[Document]:
        """Process table data into structured documents."""
        try:
            # Split content into lines and clean each line
            lines = [line for line in content.split('\n') if line.strip()]
            
            # Process each line into a structured document
            documents = []
            for line in lines:
                # Skip header-like lines
                if re.search(r'File\s*Name|SOURCE\s*TABLES|Description|Format', line, re.IGNORECASE):
                    continue
                
                # Extract fields from the line
                fields = self._extract_table_fields(line)
                
                if fields:
                    # Create a structured text representation
                    text = "Data Source Information:\n"
                    if fields.get('name'):
                        text += f"Name: {fields['name']}\n"
                    if fields.get('format'):
                        text += f"Format: {fields['format']}\n"
                    if fields.get('source'):
                        text += f"Source: {fields['source']}\n"
                    if fields.get('location'):
                        text += f"Location: {fields['location']}\n"
                    if fields.get('cadence'):
                        text += f"Update Frequency: {fields['cadence']}\n"
                    if fields.get('type'):
                        text += f"Update Type: {fields['type']}\n"
                    if fields.get('system'):
                        text += f"System: {fields['system']}\n"
                    
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "file_type": "table",
                            "is_structured": True,
                            "fields": fields
                        }
                    ))
            
            return documents
            
        except Exception as e:
            print(f"Warning: Error processing table data: {str(e)}")
            # Fall back to basic text processing
            return [Document(
                page_content=content,
                metadata={"file_type": "text", "is_structured": False}
            )]
    
    def load_documents(self, file_path: Union[str, Path]) -> List[Document]:
        """Loads and processes documents from the given file path."""
        try:
            loader = self._get_loader(file_path)
            documents = loader.load()
            
            # For structured data, preserve the structure in metadata
            if isinstance(loader, (CSVLoader, UnstructuredWordDocumentLoader)):
                processed_docs = []
                for doc in documents:
                    # Add file type and structure information to metadata
                    doc.metadata.update({
                        "file_type": Path(file_path).suffix.lower(),
                        "is_structured": True
                    })
                    processed_docs.append(doc)
                return processed_docs
            
            # For unstructured text, check if it's a table
            processed_docs = []
            for doc in documents:
                content = doc.page_content
                # Check if content looks like a table
                if any('\t' in line or '  ' in line or len(line.split()) > 3 for line in content.split('\n')):
                    table_docs = self._process_table_data(content)
                    processed_docs.extend(table_docs)
                else:
                    # Split into chunks while preserving context
                    chunks = self.text_splitter.split_text(content)
                    for i, chunk in enumerate(chunks):
                        processed_docs.append(Document(
                            page_content=chunk,
                            metadata={
                                **doc.metadata,
                                "chunk_index": i,
                                "total_chunks": len(chunks)
                            }
                        ))
            return processed_docs
            
        except Exception as e:
            raise RuntimeError(f"Error loading documents from {file_path}: {str(e)}")
    
    def load_directory(self, directory_path: Union[str, Path]) -> List[Document]:
        """Loads and processes all supported documents from a directory."""
        directory_path = Path(directory_path)
        if not directory_path.is_dir():
            raise ValueError(f"{directory_path} is not a directory")
            
        all_documents = []
        supported_extensions = {'.txt', '.pdf', '.doc', '.docx', '.md', '.html', '.htm', '.csv'}
        
        for file_path in directory_path.glob('**/*'):
            if file_path.suffix.lower() in supported_extensions:
                try:
                    documents = self.load_documents(file_path)
                    all_documents.extend(documents)
                except Exception as e:
                    print(f"Warning: Could not process {file_path}: {str(e)}")
                    continue
                    
        return all_documents
