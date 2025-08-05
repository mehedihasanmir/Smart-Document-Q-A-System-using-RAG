Smart Document Q&A System using RAG
This project is an intelligent question-answering system built on a Retrieval-Augmented Generation (RAG) architecture. It can ingest documents in various formats (PDF, DOCX, TXT, images, etc.), process their content, and accurately answer user questions based on the information contained within them.

The core purpose is to ground a Large Language Model (LLM) on a specific knowledge base, preventing hallucinations and ensuring factual, context-aware responses.

✨ Features
Multi-Format Document Support: Ingests and processes .pdf, .docx, .txt, .csv, .db (SQLite), and image files (.jpg, .png).

OCR Integration: Uses Tesseract OCR to extract text from images and scanned documents.

Multimodal Queries: Accepts both text and image-based questions.

Flexible Frontend: Can be run as a user-friendly web application using Streamlit or as a robust backend API using FastAPI.

Advanced RAG Pipeline:

Extracts content from documents.

Splits text into meaningful chunks.

Generates embeddings using sentence-transformers.

Stores and indexes vectors using faiss-cpu for fast similarity search.

Generates accurate answers using Google's Gemini model.

Containerized with Docker: Fully containerized for consistent, reproducible environments and easy deployment.

🛠️ Tech Stack
Backend: Python 3.11

UI / API: Streamlit / FastAPI

Core AI/ML:

sentence-transformers: For generating text embeddings.

faiss-cpu: For efficient similarity search (vector store).

transformers: Core library for NLP tasks.

Pillow & pytesseract: For Optical Character Recognition (OCR).

LLM: Google Gemini

Containerization: Docker

🚀 Getting Started
Follow these instructions to set up and run the project on your local machine.

1. Prerequisites
Python 3.11

Docker Desktop

Tesseract OCR Engine

Windows: Download and install from here.

macOS: brew install tesseract

Linux: sudo apt-get install tesseract-ocr

2. Local Setup
a. Clone the repository:

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

b. Create a Python Virtual Environment:

python -m venv venv

c. Activate the environment:

.\venv\Scripts\activate

pip install -r requirements.txt

e. Getting a Gemini API Key:
To use this application, you need a Google Gemini API key. You can get a free key from Google AI Studio.

Go to Google AI Studio.

Sign in with your Google account.

Click on the "Get API key" button.

Click "Create API key in new project".

Copy the generated API key.

f. Set up your environment variables:
Create a .env file in the root directory and add your newly generated Gemini API key:

GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"

3. Running the Application
You can run this project either as a Streamlit application or a FastAPI server.

Option A: Run with Streamlit (Interactive UI)

streamlit run app.py

Open your browser and go to http://localhost:8501.

Option B: Run with FastAPI (API Server)

uvicorn main:app --reload

Open your browser and go to http://127.0.0.1:8000/docs for the interactive API documentation.

🐳 Running with Docker
This project includes two separate Dockerfiles to run either the Streamlit or FastAPI application in a container.

1. Running the Streamlit App with Docker
a. Build the Docker image:

docker build -f Dockerfile.streamlit -t streamlit-rag-app .

b. Run the Docker container:

docker run -p 8501:8501 -e GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE" streamlit-rag-app

The application will be available at http://localhost:8501.

2. Running the FastAPI Server 
a. Build the Docker image:

docker build -f Dockerfile.fastapi -t fastapi-rag-api .

b. Run the Docker container:

docker run -p 8000:8000 -e GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE" fastapi-rag-api

The API will be available at http://127.0.0.1:8000.

🚢 Deployment on Docker Hub
The Streamlit application is available as a public Docker image on Docker Hub. You can pull and run it directly without building it locally.

Docker Hub Repository: https://hub.docker.com/r/mehedi88/my-rag-streamlit

a. Pull the image:

docker pull mehedi88/my-rag-streamlit:latest

b. Run the container:

docker run -p 8501:8501 -e GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE" mehedi88/my-rag-streamlit:latest

📂 Project Structure
/project-root
├── .env                  # Stores environment variables like API keys
├── app.py                # Main file for the Streamlit application
├── main.py               # Main file for the FastAPI server
├── config.py             # Loads and manages configuration from .env
├── document_processor.py # Functions for extracting text from different file types
├── rag_handler.py        # Core RAG logic (chunking, embedding, generation)
├── requirements.txt      # List of all Python dependencies
├── Dockerfile.streamlit  # Docker instructions for the Streamlit app
└── Dockerfile.fastapi    # Docker instructions for the FastAPI app
