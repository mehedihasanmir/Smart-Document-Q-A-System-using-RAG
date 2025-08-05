# rag_handler.py
import os
import faiss
import pickle
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import aiohttp

from config import settings

class RAGHandler:
    """Manages all functionalities of the RAG system."""
    def __init__(self):
        print("Loading sentence transformer model...")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print("Model loaded successfully.")
        
        self.vector_store = None
        self.text_chunks_store = []
        self.embeddings_store = []
        
        self.store_path_prefix = "vector_store"
        
        self.load_store()

    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Splits a large text into smaller chunks."""
        if not text:
            return []
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - chunk_overlap
        return chunks

    def add_document(self, text: str) -> int:
        """Processes a new document, adds it to the existing store, and rebuilds the index."""
        new_chunks = self.chunk_text(text)
        if not new_chunks:
            return 0

        print(f"Creating embeddings for {len(new_chunks)} new chunks...")
        new_embeddings = self.embedding_model.encode(new_chunks, convert_to_tensor=False)
        
        self.text_chunks_store.extend(new_chunks)
        self.embeddings_store.extend(new_embeddings)

        print(f"Rebuilding FAISS index with {len(self.text_chunks_store)} total chunks...")
        
        all_embeddings_np = np.array(self.embeddings_store).astype('float32')
        d = all_embeddings_np.shape[1]
        index = faiss.IndexFlatL2(d)
        index.add(all_embeddings_np)
        
        self.vector_store = index
        print("FAISS index rebuilt successfully.")
        return len(new_chunks)

    def save_store(self):
        """Saves the vector store and text chunks to disk."""
        if self.vector_store is None:
            print("Nothing to save.")
            return

        faiss_index_path = f"{self.store_path_prefix}.faiss"
        data_path = f"{self.store_path_prefix}_data.pkl"

        print(f"Saving FAISS index to {faiss_index_path}")
        faiss.write_index(self.vector_store, faiss_index_path)

        print(f"Saving chunks and embeddings to {data_path}")
        with open(data_path, "wb") as f:
            pickle.dump({
                "chunks": self.text_chunks_store,
                "embeddings": self.embeddings_store
            }, f)

    def load_store(self):
        """Loads the vector store and text chunks from disk if they exist."""
        faiss_index_path = f"{self.store_path_prefix}.faiss"
        data_path = f"{self.store_path_prefix}_data.pkl"

        if os.path.exists(faiss_index_path) and os.path.exists(data_path):
            print(f"Loading FAISS index from {faiss_index_path}...")
            self.vector_store = faiss.read_index(faiss_index_path)

            print(f"Loading chunks and embeddings from {data_path}...")
            with open(data_path, "rb") as f:
                data = pickle.load(f)
                self.text_chunks_store = data["chunks"]
                self.embeddings_store = data["embeddings"]
            
            print(f"Store loaded successfully. Total chunks: {len(self.text_chunks_store)}")
        else:
            print("No existing store found. Starting fresh.")

    async def get_answer(self, question: str, image_b64: Optional[str] = None, image_mime_type: Optional[str] = None) -> dict:
        """Gets an answer from the LLM using the question and relevant context."""
        if not self.vector_store:
            return {"error": "No document processed yet. Please upload a document first."}

        question_embedding = self.embedding_model.encode([question], convert_to_tensor=False)
        question_embedding = np.array(question_embedding).astype('float32')

        k = 5
        if self.vector_store.ntotal < k:
            k = self.vector_store.ntotal

        distances, indices = self.vector_store.search(question_embedding, k)
        relevant_chunks = [self.text_chunks_store[i] for i in indices[0]]
        context = "\n\n---\n\n".join(relevant_chunks)

        prompt_text = f"""
        Based on the following context from a document, and the provided image (if any), 
        please provide a clear and concise answer to the question.
        If the context does not contain the answer, state that the information is not available in the provided document.

        Context:
        ---
        {context}
        ---

        Question: {question}
        """
        
        payload_parts = [{"text": prompt_text}]
        if image_b64 and image_mime_type:
            payload_parts.append({"inline_data": {"mime_type": image_mime_type, "data": image_b64}})

        payload = {"contents": [{"parts": payload_parts}]}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(settings.GEMINI_API_URL, json=payload, headers={'Content-Type': 'application/json'}) as response:
                    response.raise_for_status()
                    result = await response.json()
                    answer = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No answer found.")
                    return {"question": question, "answer": answer, "context_chunks": relevant_chunks}
        except Exception as e:
            print(f"An exception occurred during the API call: {e}")
            error_text = await response.text()
            print(f"API Error: {response.status} - {error_text}")
            return {"error": f"An exception occurred while contacting the LLM: {e}"}

rag_handler = RAGHandler()