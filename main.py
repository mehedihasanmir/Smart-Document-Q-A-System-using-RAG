"""FastAPI application for Smart Document Q&A System using RAG."""

import os
import io
import base64
import logging
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from document_processor import FILE_EXTRACTORS, extract_text_from_sqlite
from rag_handler import rag_handler, RAGHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- FastAPI Application Setup ---
app = FastAPI(
    title="Smart Document Q&A API",
    description="REST API for document-based Q&A using OpenAI and Pinecone",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("FastAPI application initialized with CORS middleware")


def get_rag_handler() -> RAGHandler:
    """Dependency injection for RAG handler.
    
    Returns:
        RAGHandler instance
    """
    return rag_handler


# --- Root Endpoint ---
@app.get("/", tags=["Health"])
async def root() -> dict:
    """Health check endpoint.
    
    Returns:
        Greeting and API information
    """
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to Smart Document Q&A API v2.0",
        "documentation": "/docs",
        "health_status": "✅ Running"
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint with status details.
    
    Returns:
        System health status
    """
    try:
        handler = rag_handler
        chunks_count = len(handler.text_chunks_store)
        
        return {
            "status": "✅ Healthy",
            "api_version": "2.0.0",
            "knowledge_base": {
                "chunks_stored": chunks_count,
                "status": "Ready" if chunks_count > 0 else "Awaiting documents"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "❌ Unhealthy",
            "error": str(e)
        }


# --- Document Upload Endpoint ---
@app.post("/api/v1/upload", tags=["Documents"])
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    handler: RAGHandler = Depends(get_rag_handler)
) -> dict:
    """Upload and process a document.
    
    Accepts various document formats and extracts text using specialized extractors.
    The extracted text is then chunked and added to the vector store.
    
    Args:
        file: Uploaded document file
        handler: RAGHandler dependency
        
    Returns:
        Success message with processing statistics
        
    Raises:
        HTTPException: If file processing fails
    """
    try:
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()
        
        logger.info(f"Received file upload: {filename} ({file_extension})")
        
        # Validate file type
        if file_extension not in [*FILE_EXTRACTORS.keys(), ".db"]:
            error_msg = f"Unsupported file type: {file_extension}"
            logger.warning(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Read file content
        file_stream = io.BytesIO(await file.read())
        text = ""

        # Extract text based on file type
        if file_extension == ".db":
            temp_file_path = f"temp_{filename}"
            with open(temp_file_path, "wb") as f:
                f.write(file_stream.getvalue())
            text = extract_text_from_sqlite(temp_file_path)
        elif file_extension in FILE_EXTRACTORS:
            extractor = FILE_EXTRACTORS[file_extension]
            text = extractor(file_stream)
        
        # Validate extracted text
        if not text or text.isspace():
            error_msg = "No text could be extracted from the document"
            logger.warning(f"{error_msg}: {filename}")
            raise HTTPException(status_code=400, detail=error_msg)

        # Add document to RAG handler
        logger.info(f"Adding document to vector store: {filename}")
        total_new_chunks = handler.add_document(text)
        
        if total_new_chunks == 0:
            error_msg = "Document content was too short to be processed"
            logger.warning(f"{error_msg}: {filename}")
            raise HTTPException(status_code=400, detail=error_msg)

        logger.info(f"Successfully processed {filename}: {total_new_chunks} chunks added")
        
        return {
            "status": "success",
            "message": f"Successfully processed and indexed '{filename}'.",
            "file_name": filename,
            "new_chunks_added": total_new_chunks,
            "total_chunks_in_knowledge_base": len(handler.text_chunks_store)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error processing {file.filename}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


# --- Query Endpoint ---
@app.post("/api/v1/query", tags=["Query"])
async def query_document(
    question: str = Form(..., description="Your question about the documents"),
    image_query: Optional[UploadFile] = File(None, description="Optional image to include in query"),
    handler: RAGHandler = Depends(get_rag_handler)
) -> dict:
    """Ask a question about uploaded documents.
    
    Uses RAG to retrieve relevant document chunks and generate an answer
    using OpenAI's GPT-4 model.
    
    Args:
        question: User's question
        image_query: Optional image file for visual context
        handler: RAGHandler dependency
        
    Returns:
        Answer and source context chunks
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        logger.info(f"Processing query: {question[:50]}...")
        
        # Validate input
        if not question.strip():
            error_msg = "Question cannot be empty"
            logger.warning(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        if len(handler.text_chunks_store) == 0:
            error_msg = "No documents uploaded. Please upload documents first."
            logger.warning(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

        # Process image if provided
        image_b64 = None
        image_mime_type = None
        
        if image_query:
            if not image_query.content_type.startswith("image/"):
                error_msg = "Provided file must be an image"
                logger.warning(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)
            
            image_bytes = await image_query.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            image_mime_type = image_query.content_type
            logger.debug(f"Image included in query: {image_mime_type}")

        # Get answer using RAG
        logger.info("Calling RAG handler for answer generation")
        result = await handler.get_answer(question, image_b64, image_mime_type)
        
        if "error" in result:
            logger.warning(f"RAG query returned error: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info("Successfully generated answer")
        
        return {
            "status": "success",
            "question": result.get("question"),
            "answer": result.get("answer"),
            "source_chunks": result.get("context_chunks", []),
            "chunks_used": len(result.get("context_chunks", []))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error processing query: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


# --- Statistics Endpoint ---
@app.get("/api/v1/stats", tags=["Statistics"])
async def get_statistics(handler: RAGHandler = Depends(get_rag_handler)) -> dict:
    """Get knowledge base statistics.
    
    Args:
        handler: RAGHandler dependency
        
    Returns:
        Statistics about the stored documents and chunks
    """
    try:
        logger.info("Statistics endpoint accessed")
        
        chunks_count = len(handler.text_chunks_store)
        
        return {
            "status": "success",
            "statistics": {
                "total_chunks": chunks_count,
                "knowledge_base_status": "Ready" if chunks_count > 0 else "Empty",
                "api_version": "2.0.0",
                "vector_db": "Pinecone",
                "embedding_model": "text-embedding-3-small",
                "llm_model": "gpt-4-turbo"
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Error Handlers ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """General exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "An unexpected error occurred",
            "details": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting FastAPI server")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
