# 📄 Smart Document Q&A System using RAG

An intelligent question-answering system built on a **Retrieval-Augmented Generation (RAG)** architecture. It can ingest documents in various formats (PDF, DOCX, TXT, images, etc.), process their content, and accurately answer user questions based on the information contained within them.

The core purpose is to ground a Large Language Model (LLM) on a specific knowledge base, preventing hallucinations and ensuring factual, context-aware responses.

---

## ✨ Features

- **Multi-Format Document Support:** Supports `.pdf`, `.docx`, `.txt`, `.csv`, `.db (SQLite)`, and image files (`.jpg`, `.png`).
- **OCR Integration:** Extracts text from images using Tesseract OCR.
- **Multimodal Queries:** Accepts both text and image-based questions.
- **Flexible Interface:** 
  - Streamlit for interactive web UI
  - FastAPI for robust backend API
- **Advanced RAG Pipeline:**
  - Extracts and preprocesses content
  - Chunks text for processing
  - Generates embeddings using SentenceTransformers
  - Stores vectors using FAISS for similarity search
  - Produces answers with **Google Gemini**
- **Containerized with Docker:** Easy deployment and consistent environments

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11
- **UI / API:** Streamlit / FastAPI
- **Core AI/ML:**
  - `sentence-transformers` – Text embeddings
  - `faiss-cpu` – Vector similarity search
  - `transformers` – NLP tasks
  - `pytesseract` & `Pillow` – OCR
  - `Google Gemini API` – LLM for answer generation
- **Containerization:** Docker

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.11
- Docker Desktop
- Tesseract OCR Engine:
  - **Windows:** Download and install from [here](https://github.com/tesseract-ocr/tesseract)
  - **macOS:** `brew install tesseract`
  - **Linux:** `sudo apt-get install tesseract-ocr`

---

### ⚙️ Configure Tesseract Path (Windows only)

If you're using Windows, you may need to explicitly specify the Tesseract executable path in your Python code:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Or, add the Tesseract installation directory to your system's environment variables so this is done automatically.

---

### 🔧 Local Setup

```bash
# Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# Create a virtual environment
python -m venv venv

# Activate the environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 🔑 Get a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app)
2. Sign in with your Google account
3. Click **"Get API key"**
4. Click **"Create API key in new project"**
5. Copy the generated API key

Create a `.env` file in the root directory and add:

```env
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

---

## 🧪 Running the Application

### Option A: Streamlit (UI)
```bash
streamlit run app.py
```
Visit: [http://localhost:8501](http://localhost:8501)

### Option B: FastAPI (Backend API)
```bash
uvicorn main:app --reload
```
Visit: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🐳 Docker Setup

### ✅ Streamlit App

```bash
# Build the Docker image
docker build -f Dockerfile.streamlit -t streamlit-rag-app .

# Run the container
docker run -p 8501:8501 -e GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE" streamlit-rag-app
```

Visit: [http://localhost:8501](http://localhost:8501)

### ✅ FastAPI Server

```bash
# Build the Docker image
docker build -f Dockerfile.fastapi -t fastapi-rag-api .

# Run the container
docker run -p 8000:8000 -e GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE" fastapi-rag-api
```

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🚢 Deployment via Docker Hub

The Streamlit version is publicly available on Docker Hub:

**Docker Hub Repo:** [mehedi88/my-rag-streamlit](https://hub.docker.com/r/mehedi88/my-rag-streamlit)

```bash
# Pull the image
docker pull mehedi88/my-rag-streamlit:latest

# Run the container
docker run -p 8501:8501 -e GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE" mehedi88/my-rag-streamlit:latest
```

---

## 📂 Project Structure

```
/project-root
├── .env                      # Stores environment variables like API keys
├── app.py                   # Main file for the Streamlit application
├── main.py                  # Main file for the FastAPI server
├── config.py                # Loads and manages configuration from .env
├── document_processor.py    # Functions for extracting text from different file types
├── rag_handler.py           # Core RAG logic (chunking, embedding, generation)
├── requirements.txt         # List of Python dependencies
├── Dockerfile.streamlit     # Docker instructions for Streamlit
└── Dockerfile.fastapi       # Docker instructions for FastAPI
```

---

## 📬 Contribution

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---


## 🙏 Acknowledgments

- Google Gemini
- HuggingFace Transformers & SentenceTransformers
- Tesseract OCR
- FAISS by Facebook AI

---

Feel free to ⭐️ this repo if you find it useful!