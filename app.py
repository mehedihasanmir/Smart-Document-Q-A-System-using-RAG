# app.py
import streamlit as st
import os
import io
import base64
import asyncio

# Import from modular files
from document_processor import FILE_EXTRACTORS, extract_text_from_sqlite
from rag_handler import RAGHandler

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Smart Document Q&A",
    layout="wide"
)

st.title("Smart Document Q&A")
st.write("Upload any document and ask questions about its content. You can even include images in your questions!")

# --- Session State Initialization ---
# This holds the RAGHandler object across the entire session.
if 'rag_handler' not in st.session_state:
    st.session_state.rag_handler = RAGHandler()

# --- Helper function to run async code ---
def run_async(coro):
    """A helper to run async functions from Streamlit."""
    return asyncio.run(coro)

# --- UI Layout ---
col1, col2 = st.columns(2)

# --- Column 1: Document Upload ---
with col1:
    st.header("Step 1: Upload Your Document(s)")
    uploaded_document = st.file_uploader(
        "Select a document (.pdf, .docx, .txt, .jpg, .png, .csv, .db)",
        type=['pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'csv', 'db']
    )

    if uploaded_document is not None:
        with st.spinner('Processing document... Please wait.'):
            file_extension = os.path.splitext(uploaded_document.name)[1].lower()
            
            text = ""
            if file_extension == ".db":
                # Save temp file for SQLite processing
                temp_file_path = f"temp_{uploaded_document.name}"
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_document.getvalue())
                text = extract_text_from_sqlite(temp_file_path)
            elif file_extension in FILE_EXTRACTORS:
                file_stream = io.BytesIO(uploaded_document.read())
                extractor = FILE_EXTRACTORS[file_extension]
                text = extractor(file_stream)
            
            if text:
                handler = st.session_state.rag_handler
                total_chunks = handler.add_document(text) # Use add_document
                handler.save_store() # Save state after adding
                st.success(f"Document '{uploaded_document.name}' processed successfully! New chunks added: {total_chunks}")
                st.info(f"Total documents processed in this session: {len(handler.text_chunks_store)} chunks.")
            else:
                st.error("Could not extract any text from the document.")

# --- Column 2: Query Section ---
with col2:
    st.header("Step 2: Ask a Question")
    
    question_text = st.text_area("Your Question:", height=100, placeholder="e.g., What is the main conclusion of the document?")
    
    uploaded_image_query = st.file_uploader(
        "Add an image to your question (optional)",
        type=['jpg', 'jpeg', 'png']
    )

    if st.button("Get Answer", type="primary"):
        handler = st.session_state.rag_handler
        if not question_text:
            st.warning("Please enter a question.")
        elif handler.vector_store is None:
            st.error("Please upload and process at least one document first.")
        else:
            with st.spinner("Finding the best answer..."):
                image_b64 = None
                image_mime_type = None
                if uploaded_image_query:
                    image_bytes = uploaded_image_query.read()
                    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                    image_mime_type = uploaded_image_query.type

                result = run_async(handler.get_answer(question_text, image_b64, image_mime_type))

                st.divider()
                st.subheader("Answer:")
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.write(result.get("answer", "No answer found."))
                    
                    with st.expander("Show Context Chunks"):
                        st.json(result.get("context_chunks", []))