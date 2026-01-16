# Smart Document Q&A System using RAG

A professional-grade document question-answering system powered by OpenAI GPT-4 and Pinecone vector database.

## Features

- 📄 **Multi-format Document Support**: PDF, DOCX, TXT, PNG, JPG, CSV, and SQLite databases
- 🤖 **AI-Powered Answers**: Uses OpenAI GPT-4 Turbo for intelligent responses
- 🔍 **Advanced Retrieval**: Pinecone vector database for efficient semantic search
- 🖼️ **Multimodal Queries**: Ask questions with images for visual context
- 📊 **Production-Ready**: Professional error handling, logging, and type hints
- 🚀 **Dual Interface**: Both Streamlit UI and FastAPI REST endpoints

## Architecture

```
Document Upload
     ↓
Text Extraction (Multiple Formats)
     ↓
Text Chunking (Overlapping Chunks)
     ↓
OpenAI Embeddings
     ↓
Pinecone Vector Store
     ↓
Semantic Search & RAG
     ↓
GPT-4 Answer Generation
```

## Prerequisites

- Python 3.8+
- OpenAI API Key ([Get here](https://platform.openai.com/api-keys))
- Pinecone API Key ([Get here](https://www.pinecone.io/))

## Installation

1. **Clone the repository:**
```bash
cd Smart-Document-Q-A-System-using-RAG
```

2. **Create a virtual environment:**
```bash
python -m venv myvenv
source myvenv/bin/activate  # On Windows: myvenv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=your_environment_here
```

## Usage

### Option 1: Streamlit Web Interface

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Option 2: FastAPI REST API

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then visit `http://localhost:8000/docs` for interactive API documentation

## API Endpoints

### Health Check
```
GET /health
```

### Upload Document
```
POST /api/v1/upload
Content-Type: multipart/form-data

Body:
  file: [binary file data]
```

### Query Documents
```
POST /api/v1/query
Content-Type: multipart/form-data

Body:
  question: "Your question here"
  image_query: [optional image file]
```

### Get Statistics
```
GET /api/v1/stats
```

## Configuration

Edit `.env` to customize:

```env
# Chunk size for text processing
CHUNK_SIZE=1000

# Overlap between chunks for better context
CHUNK_OVERLAP=200

# Number of results to retrieve
TOP_K_RESULTS=5

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

## Project Structure

```
├── app.py                    # Streamlit web interface
├── main.py                   # FastAPI REST API
├── config.py                 # Configuration management
├── rag_handler.py            # RAG logic with OpenAI & Pinecone
├── document_processor.py     # Document text extraction
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Module Documentation

### config.py
Configuration settings with validation. Loads from `.env` file.

**Key Classes:**
- `Settings`: Configuration with environment variable validation

### document_processor.py
Text extraction from various file formats.

**Key Functions:**
- `extract_text_from_pdf()`: PDF text extraction
- `extract_text_from_docx()`: Word document parsing
- `extract_text_from_txt()`: Plain text reading
- `extract_text_from_image()`: OCR using Tesseract
- `extract_text_from_csv()`: CSV file processing
- `extract_text_from_sqlite()`: Database data extraction

### rag_handler.py
Core RAG implementation with OpenAI and Pinecone integration.

**Key Classes:**
- `RAGHandler`: Manages chunking, embeddings, vector storage, and QA

**Key Methods:**
- `chunk_text()`: Split documents into overlapping chunks
- `add_document()`: Process and store documents
- `get_answer()`: Retrieve context and generate answers

### app.py
Streamlit web interface for interactive document Q&A.

**Features:**
- File upload with progress indication
- Real-time document processing
- Interactive question-answer interface
- Knowledge base statistics
- Source document display

### main.py
FastAPI REST API for programmatic access.

**Endpoints:**
- `/`: Root endpoint with API info
- `/health`: System health check
- `/api/v1/upload`: Document upload
- `/api/v1/query`: Query documents
- `/api/v1/stats`: Knowledge base statistics

## Error Handling

The system includes comprehensive error handling:

- **Validation**: File type and content validation
- **Logging**: Detailed logging at all levels
- **API Errors**: Graceful handling of OpenAI and Pinecone API errors
- **User Feedback**: Clear error messages in UI and API responses

## Logging

Logs are written to console with the following format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Configure log level via `LOG_LEVEL` environment variable.

## Performance

- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **LLM**: OpenAI GPT-4 Turbo with 1000 token limit
- **Vector Search**: Pinecone with cosine similarity
- **Chunk Optimization**: 1000 character chunks with 200 character overlap

## Security

- API keys stored in `.env` (not in version control)
- CORS enabled for development (restrict in production)
- Input validation on all endpoints
- Secure error handling without sensitive info leakage

## Dependencies

- **fastapi**: Web framework
- **streamlit**: Web UI
- **openai==1.12.0**: OpenAI API client (pinned for compatibility)
- **pinecone-client==3.0.0**: Pinecone vector database client (pinned)
- **httpx==0.24.1**: HTTP client (pinned for OpenAI compatibility)
- **pypdf**: PDF processing
- **python-docx**: Word document processing
- **Pillow & pytesseract**: Image OCR
- **python-dotenv**: Environment configuration

See `requirements.txt` for all dependencies and versions.

### Important Version Notes
The OpenAI and httpx versions are pinned to ensure compatibility. OpenAI 1.12.0 requires httpx 0.24.1 to avoid the `proxies` parameter error. Do not upgrade these packages independently without testing.

## Docker Support

Build and run with Docker:

```bash
docker build -t smart-rag .
docker run -p 8501:8501 -p 8000:8000 --env-file .env smart-rag
```

## Troubleshooting

**Issue: "OPENAI_API_KEY is not set"**
- Ensure `.env` file exists with valid API key
- Verify key is active in OpenAI dashboard

**Issue: "Pinecone index not found"**
- Check Pinecone environment variable matches your setup
- Ensure API key has proper permissions

**Issue: "Client.__init__() got an unexpected keyword argument 'proxies'"**
- This is a version compatibility issue
- Ensure you have the correct versions: `openai==1.12.0` and `httpx==0.24.1`
- Run: `pip install openai==1.12.0 httpx==0.24.1 pinecone-client==3.0.0`
- Restart your application after installing

**Issue: Tesseract not found for OCR**
- Install Tesseract: `choco install tesseract` (Windows) or `brew install tesseract` (Mac)
- Set PATH if custom installation

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in console output
3. Check OpenAI and Pinecone API status
4. Verify environment configuration

## Future Enhancements

- [ ] Multi-language support
- [ ] Document summarization
- [ ] Batch processing
- [ ] Custom embeddings models
- [ ] Advanced caching
- [ ] Real-time document streaming

---

**Built with OpenAI GPT-4 | Pinecone | FastAPI | Streamlit**
