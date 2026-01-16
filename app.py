"""Streamlit application for Smart Document Q&A System using RAG."""

import streamlit as st
import os
import io
import base64
import asyncio
import logging
from typing import Optional, Tuple

from document_processor import FILE_EXTRACTORS, extract_text_from_sqlite
from rag_handler import rag_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Smart Document Q&A System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 Smart Document Q&A System")
st.markdown("### Powered by OpenAI and Pinecone")
st.write("Upload documents and ask questions to get intelligent answers based on the content.")

# --- Session State Initialization ---
if 'rag_handler' not in st.session_state:
    st.session_state.rag_handler = rag_handler
    logger.info("RAG Handler initialized in session state")

if 'processed_count' not in st.session_state:
    st.session_state.processed_count = len(rag_handler.text_chunks_store)


def run_async(coro):
    """Helper function to run async code in Streamlit.
    
    Args:
        coro: Coroutine to execute
        
    Returns:
        Result of the coroutine
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


def process_uploaded_file(uploaded_file) -> Tuple[str, int]:
    """Process an uploaded file and extract text.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Tuple of (extracted text, number of chunks added)
        
    Raises:
        ValueError: If file processing fails
    """
    try:
        filename = uploaded_file.name
        file_extension = os.path.splitext(filename)[1].lower()
        
        logger.info(f"Processing file: {filename} ({file_extension})")
        
        text = ""
        
        if file_extension == ".db":
            # Handle SQLite database
            temp_file_path = f"temp_{filename}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            text = extract_text_from_sqlite(temp_file_path)
            
        elif file_extension in FILE_EXTRACTORS:
            # Handle supported file types
            file_stream = io.BytesIO(uploaded_file.read())
            extractor = FILE_EXTRACTORS[file_extension]
            text = extractor(file_stream)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        if not text or text.isspace():
            raise ValueError("No text could be extracted from the document")
        
        # Add document to RAG handler
        handler = st.session_state.rag_handler
        total_chunks = handler.add_document(text)
        
        logger.info(f"Successfully processed {filename}: {total_chunks} chunks added")
        return text, total_chunks
        
    except Exception as e:
        logger.error(f"Error processing file {uploaded_file.name}: {str(e)}")
        raise


# --- UI Layout ---
col1, col2 = st.columns(2)

# --- Column 1: Document Upload ---
with col1:
    st.header("📤 Step 1: Upload Documents")
    
    uploaded_file = st.file_uploader(
        "Select a document to upload",
        type=['pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'csv', 'db'],
        help="Supported formats: PDF, DOCX, TXT, JPG, PNG, CSV, SQLite DB"
    )

    if uploaded_file is not None:
        with st.spinner('⏳ Processing document... Please wait.'):
            try:
                text, chunks_added = process_uploaded_file(uploaded_file)
                st.success(f"✅ Document '{uploaded_file.name}' processed successfully!")
                st.info(f"📊 Added {chunks_added} chunks to the knowledge base")
                
                # Update session state
                st.session_state.processed_count = len(rag_handler.text_chunks_store)
                
            except ValueError as e:
                st.error(f"❌ Error processing document: {str(e)}")
                logger.error(f"File processing error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                logger.error(f"Unexpected error during file processing: {str(e)}")
    
    # Display statistics
    st.divider()
    st.subheader("📈 Knowledge Base Statistics")
    col1_stat, col2_stat = st.columns(2)
    
    with col1_stat:
        total_chunks = len(rag_handler.text_chunks_store)
        st.metric("Total Chunks", total_chunks)
    
    with col2_stat:
        st.metric("Status", "✅ Ready" if total_chunks > 0 else "⏳ Waiting")


# --- Column 2: Query Section ---
with col2:
    st.header("❓ Step 2: Ask a Question")
    
    question_text = st.text_area(
        "Enter your question:",
        height=100,
        placeholder="e.g., What is the main conclusion of the document?",
        help="Type your question here to get answers based on uploaded documents"
    )
    
    uploaded_image = st.file_uploader(
        "📸 Add an image to your question (optional)",
        type=['jpg', 'jpeg', 'png'],
        help="Include an image if your question relates to visual content"
    )

    if st.button("🔍 Get Answer", type="primary", use_container_width=True):
        handler = st.session_state.rag_handler
        
        # Validation
        if not question_text.strip():
            st.warning("⚠️ Please enter a question.")
        elif len(handler.text_chunks_store) == 0:
            st.error("❌ Please upload and process at least one document first.")
        else:
            with st.spinner("🤖 Finding the best answer..."):
                try:
                    # Prepare image data if provided
                    image_b64 = None
                    image_mime_type = None
                    
                    if uploaded_image:
                        image_bytes = uploaded_image.read()
                        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                        image_mime_type = uploaded_image.type
                        logger.info(f"Including image in query: {image_mime_type}")

                    # Get answer using RAG
                    result = run_async(handler.get_answer(
                        question_text, 
                        image_b64, 
                        image_mime_type
                    ))

                    st.divider()
                    
                    if "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                        logger.error(f"RAG query error: {result['error']}")
                    else:
                        # Display results
                        st.subheader("✅ Answer:")
                        st.write(result.get("answer", "No answer found."))
                        
                        # Display context chunks
                        with st.expander("📚 View Source Documents"):
                            chunks = result.get("context_chunks", [])
                            if chunks:
                                for i, chunk in enumerate(chunks, 1):
                                    st.markdown(f"**Chunk {i}:**")
                                    st.text(chunk[:500] + "..." if len(chunk) > 500 else chunk)
                                    st.divider()
                            else:
                                st.info("No source documents available")
                        
                        logger.info("Successfully generated answer")
                        
                except Exception as e:
                    st.error(f"❌ Unexpected error while generating answer: {str(e)}")
                    logger.error(f"Unexpected error in get_answer: {str(e)}")

# --- Footer ---
st.divider()
st.markdown("""
    ---
    **Smart Document Q&A System** | Powered by OpenAI GPT-4 & Pinecone Vector DB
    
    Built with [Streamlit](https://streamlit.io/) | [FastAPI](https://fastapi.tiangolo.com/) | [OpenAI](https://openai.com/) | [Pinecone](https://www.pinecone.io/)
""")
