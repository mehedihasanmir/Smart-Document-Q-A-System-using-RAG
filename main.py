# main.py
import os
import io
import base64
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from document_processor import FILE_EXTRACTORS, extract_text_from_sqlite
from rag_handler import rag_handler, RAGHandler

app = FastAPI(
    title="Smart RAG API",
    description="A modular API for document-based Q&A.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_rag_handler():
    return rag_handler

@app.post("/upload/", summary="Upload and process a document")
async def upload_document(file: UploadFile = File(...), handler: RAGHandler = Depends(get_rag_handler)):
    """Accepts a document, extracts text, and adds it to the vector store."""
    filename = file.filename
    file_extension = os.path.splitext(filename)[1].lower()
    
    print(f"Received file: {filename} (type: {file_extension})")
    
    file_stream = io.BytesIO(await file.read())
    text = ""

    if file_extension == ".db":
        temp_file_path = f"temp_{filename}"
        with open(temp_file_path, "wb") as f:
            f.write(file_stream.getvalue())
        text = extract_text_from_sqlite(temp_file_path)
    elif file_extension in FILE_EXTRACTORS:
        extractor = FILE_EXTRACTORS[file_extension]
        text = extractor(file_stream)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
    
    if not text or text.isspace():
        raise HTTPException(status_code=400, detail="No text could be extracted from the document.")

    total_new_chunks = handler.add_document(text)
    
    if total_new_chunks == 0:
        raise HTTPException(status_code=400, detail="Document content was too short to be processed.")

    handler.save_store()
        
    return {
        "message": f"Successfully processed and added '{filename}'.", 
        "new_chunks_added": total_new_chunks,
        "total_chunks_in_store": len(handler.text_chunks_store)
    }

@app.post("/query/", summary="Ask a question about the uploaded document(s)")
async def query_document(
    question: str = Form(...),
    image_query: Optional[UploadFile] = File(None),
    handler: RAGHandler = Depends(get_rag_handler)
):
    """Accepts a text question and an optional image, then returns an answer."""
    image_b64 = None
    image_mime_type = None
    if image_query:
        if not image_query.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Image query file must be an image.")
        image_bytes = await image_query.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        image_mime_type = image_query.content_type

    result = await handler.get_answer(question, image_b64, image_mime_type)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@app.get("/", summary="Root endpoint")
async def root():
    return {"message": "Welcome to the Smart RAG API v2.0!"}