"""RAG (Retrieval-Augmented Generation) handler using OpenAI and Pinecone."""

import logging
from typing import List, Optional, Dict, Any
import os

from openai import OpenAI, APIError, APIConnectionError
from pinecone import Pinecone, ServerlessSpec

from config import settings

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class RAGHandler:
    """Manages Retrieval-Augmented Generation using OpenAI and Pinecone.
    
    This class handles document chunking, embedding generation, vector storage,
    and retrieval-augmented question answering using OpenAI GPT models.
    """
    
    def __init__(self) -> None:
        """Initialize RAG handler with OpenAI and Pinecone clients."""
        try:
            logger.info("Initializing RAG Handler")
            
            # Initialize OpenAI client
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info(f"OpenAI client initialized with model: {settings.OPENAI_LLM_MODEL}")
            
            # Initialize Pinecone client
            self.pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Get or create Pinecone index
            self._initialize_pinecone_index()
            
            # Store configuration
            self.chunk_size = settings.CHUNK_SIZE
            self.chunk_overlap = settings.CHUNK_OVERLAP
            self.top_k = settings.TOP_K_RESULTS
            
            # In-memory store for chunks (for reference)
            self.text_chunks_store: List[str] = []
            
            logger.info("RAG Handler initialized successfully")
            
        except APIError as e:
            logger.error(f"OpenAI API error during initialization: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error initializing RAG Handler: {str(e)}")
            raise
    
    def _initialize_pinecone_index(self) -> None:
        """Initialize or connect to Pinecone index.
        
        Raises:
            Exception: If Pinecone index initialization fails
        """
        try:
            logger.info(f"Initializing Pinecone index: {settings.PINECONE_INDEX_NAME}")
            
            # Check if index exists
            existing_indexes = self.pinecone_client.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if settings.PINECONE_INDEX_NAME not in index_names:
                logger.info(f"Creating new Pinecone index: {settings.PINECONE_INDEX_NAME}")
                self.pinecone_client.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=1536,  # OpenAI text-embedding-3-small dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            
            self.index = self.pinecone_client.Index(settings.PINECONE_INDEX_NAME)
            logger.info("Pinecone index initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone index: {str(e)}")
            raise
    
    def chunk_text(self, text: str, chunk_size: Optional[int] = None, 
                   chunk_overlap: Optional[int] = None) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: Text to split into chunks
            chunk_size: Size of each chunk (uses config if not provided)
            chunk_overlap: Overlap between consecutive chunks
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        chunk_size = chunk_size or self.chunk_size
        chunk_overlap = chunk_overlap or self.chunk_overlap
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - chunk_overlap
        
        logger.debug(f"Text split into {len(chunks)} chunks")
        return chunks
    
    def add_document(self, text: str) -> int:
        """Process and add a document to the vector store.
        
        Args:
            text: Document text to add
            
        Returns:
            Number of chunks added
            
        Raises:
            APIError: If OpenAI API call fails
        """
        try:
            logger.info("Processing new document")
            
            # Chunk the text
            new_chunks = self.chunk_text(text)
            if not new_chunks:
                logger.warning("No chunks created from document")
                return 0
            
            logger.info(f"Creating embeddings for {len(new_chunks)} chunks")
            
            # Generate embeddings using OpenAI
            embeddings_response = self.openai_client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=new_chunks
            )
            
            embeddings = [item.embedding for item in embeddings_response.data]
            logger.debug(f"Successfully generated {len(embeddings)} embeddings")
            
            # Prepare vectors for Pinecone
            vectors_to_upsert = []
            for i, (chunk, embedding) in enumerate(zip(new_chunks, embeddings)):
                vector_id = f"chunk_{len(self.text_chunks_store) + i}"
                vectors_to_upsert.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {"text": chunk}
                })
            
            # Upsert to Pinecone
            logger.info(f"Upserting {len(vectors_to_upsert)} vectors to Pinecone")
            self.index.upsert(vectors=vectors_to_upsert)
            
            # Store chunks locally for reference
            self.text_chunks_store.extend(new_chunks)
            
            logger.info(f"Successfully added {len(new_chunks)} chunks. Total chunks: {len(self.text_chunks_store)}")
            return len(new_chunks)
            
        except APIError as e:
            logger.error(f"OpenAI API error during document processing: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    async def get_answer(self, question: str, image_b64: Optional[str] = None, 
                        image_mime_type: Optional[str] = None) -> Dict[str, Any]:
        """Get an answer to a question using RAG.
        
        Args:
            question: User's question
            image_b64: Optional base64 encoded image
            image_mime_type: MIME type of the image
            
        Returns:
            Dictionary containing question, answer, and context chunks
        """
        try:
            if len(self.text_chunks_store) == 0:
                error_msg = "No documents processed yet. Please upload a document first."
                logger.warning(error_msg)
                return {"error": error_msg}
            
            logger.info(f"Processing question: {question}")
            
            # Generate embedding for the question
            logger.debug("Generating embedding for question")
            question_embedding_response = self.openai_client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=question
            )
            question_embedding = question_embedding_response.data[0].embedding
            
            # Search Pinecone for relevant chunks
            logger.debug(f"Searching for top {self.top_k} similar chunks")
            search_results = self.index.query(
                vector=question_embedding,
                top_k=self.top_k,
                include_metadata=True
            )
            
            # Extract relevant chunks
            relevant_chunks = [
                match["metadata"]["text"] 
                for match in search_results["matches"] 
                if "metadata" in match and "text" in match["metadata"]
            ]
            
            if not relevant_chunks:
                logger.warning("No relevant chunks found for question")
                return {"error": "No relevant information found in documents"}
            
            context = "\n\n---\n\n".join(relevant_chunks)
            
            # Build the prompt
            system_message = """You are a helpful assistant that answers questions based on provided context. 
If the context doesn't contain the answer, clearly state that the information is not available in the provided documents.
Provide clear, concise, and accurate answers."""
            
            # Build content with text and optional image
            content = [
                {
                    "type": "text",
                    "text": f"""Based on the following context from documents, please answer the question.

Context:
---
{context}
---

Question: {question}"""
                }
            ]
            
            if image_b64 and image_mime_type:
                logger.debug("Including image in question")
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{image_mime_type};base64,{image_b64}"
                    }
                })
            
            # Call OpenAI API
            logger.info(f"Calling OpenAI API with model: {settings.OPENAI_LLM_MODEL}")
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            logger.info("Successfully generated answer")
            
            return {
                "question": question,
                "answer": answer,
                "context_chunks": relevant_chunks
            }
            
        except APIConnectionError as e:
            error_msg = f"Failed to connect to OpenAI API: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except APIError as e:
            error_msg = f"OpenAI API error: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error generating answer: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}


# Global RAG handler instance
rag_handler = RAGHandler()
