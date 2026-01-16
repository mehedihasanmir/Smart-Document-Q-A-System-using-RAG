# Quick Reference Guide

## Project Structure

```
📦 Smart Document Q&A System
├── 🎨 Frontend & APIs
│   ├── app.py                    # Streamlit Web UI
│   └── main.py                   # FastAPI REST API
├── 🧠 Core Logic
│   ├── rag_handler.py            # RAG implementation
│   └── document_processor.py     # Text extraction
├── ⚙️ Configuration
│   ├── config.py                 # Settings & validation
│   ├── .env.example              # Environment template
│   └── requirements.txt           # Dependencies
├── 📚 Documentation
│   ├── README.md                 # Project overview
│   ├── SETUP.md                  # Installation guide
│   ├── MIGRATION.md              # From Gemini→OpenAI
│   └── SUMMARY.md                # Update summary
└── 🐳 Deployment
    ├── Dockerfile                # Container image
    └── docker-compose.yml        # Orchestration
```

## Quick Start Commands

### Setup (5 minutes)
```bash
# 1. Clone repository
cd Smart-Document-Q-A-System-using-RAG

# 2. Virtual environment
python -m venv myvenv
source myvenv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Edit .env with your API keys
```

### Run Streamlit UI
```bash
streamlit run app.py
# Open: http://localhost:8501
```

### Run FastAPI
```bash
python -m uvicorn main:app --reload
# Open: http://localhost:8000/docs
```

### Docker
```bash
docker-compose up --build
```

## Environment Variables

```env
# Required: OpenAI
OPENAI_API_KEY=sk-proj-...          # From https://platform.openai.com/api-keys

# Required: Pinecone
PINECONE_API_KEY=pcsk_...           # From https://www.pinecone.io/
PINECONE_ENVIRONMENT=us-east-1-aws  # From Pinecone console

# Optional: Models
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-4-turbo

# Optional: Tuning
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
LOG_LEVEL=INFO
```

## API Endpoints

### Root & Health
```bash
# Welcome
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health
```

### Documents
```bash
# Upload
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@document.pdf"

# Query
curl -X POST http://localhost:8000/api/v1/query \
  -F "question=What is this?"

# Stats
curl http://localhost:8000/api/v1/stats
```

## Key Features

### Streamlit App
- 📄 Multi-format document upload (PDF, DOCX, TXT, PNG, CSV, SQLite)
- 💬 Interactive Q&A interface
- 📊 Knowledge base statistics
- 📚 Source document viewer
- 🔍 Multimodal queries (text + images)

### FastAPI API
- 📚 RESTful document management
- 🤖 AI-powered QA
- 📈 Real-time statistics
- 🔒 Error handling & validation
- 📖 Auto-generated API docs

### Backend
- 🧠 OpenAI GPT-4 for answers
- 🔍 OpenAI embeddings for semantic search
- 📌 Pinecone for vector storage
- 📦 Automatic document chunking
- 🔄 Cloud-native architecture

## Supported File Types

| Format | Extension | Handler |
|--------|-----------|---------|
| PDF | `.pdf` | PyPDF |
| Word | `.docx` | python-docx |
| Text | `.txt` | Built-in |
| Image | `.jpg, .png` | Tesseract OCR |
| Data | `.csv` | CSV parser |
| Database | `.db` | SQLite |

## Configuration Options

### Chunking Strategy
```env
CHUNK_SIZE=1000        # Larger = fewer embeddings, less context
CHUNK_OVERLAP=200      # Larger = better context continuity
```

### Vector Search
```env
TOP_K_RESULTS=5        # More = slower but better coverage
```

### Models
```env
OPENAI_LLM_MODEL=gpt-4-turbo  # Best quality
OPENAI_EMBEDDING_MODEL=text-embedding-3-small  # Good balance
```

## Troubleshooting

### API Keys Not Found
```bash
# Check .env exists
ls -la .env

# Verify keys are set
cat .env | grep API_KEY

# Reinstall dotenv
pip install --force-reinstall python-dotenv
```

### Version Compatibility Issues
```bash
# Fix "proxies" parameter error
pip install openai==1.12.0 httpx==0.24.1 pinecone-client==3.0.0 --force-reinstall

# Verify versions
pip list | grep -E "openai|httpx|pinecone"
```

### Port Already in Use
```bash
# Streamlit on 8502
streamlit run app.py --server.port 8502

# FastAPI on 8001
python -m uvicorn main:app --port 8001
```

### Tesseract Not Found
```bash
# Windows (choco)
choco install tesseract

# macOS
brew install tesseract

# Linux
sudo apt-get install tesseract-ocr
```

### Rate Limit Error
- Check OpenAI usage dashboard
- Upgrade API plan if needed
- Implement retry logic
- Reduce concurrent requests

## Development Tips

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed info")
logger.info("General info")
logger.warning("Warning")
logger.error("Error")
```

### Async Operations
```python
import asyncio

# Run async function
result = await handler.get_answer(question, image_b64, mime_type)

# In sync code (Streamlit)
result = asyncio.run(handler.get_answer(question, None, None))
```

### Error Handling
```python
from openai import APIError, APIConnectionError

try:
    response = client.chat.completions.create(...)
except APIError as e:
    logger.error(f"API error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

## Performance Tuning

### For Speed
```env
CHUNK_SIZE=500         # Smaller chunks = faster
TOP_K_RESULTS=3        # Fewer results = faster
```

### For Quality
```env
CHUNK_SIZE=1500        # Larger chunks = more context
TOP_K_RESULTS=10       # More results = better coverage
```

### For Cost
```env
OPENAI_EMBEDDING_MODEL=text-embedding-3-small  # Cheaper
OPENAI_LLM_MODEL=gpt-3.5-turbo                  # Faster, cheaper
```

## Monitoring

### Check Application Logs
```bash
# Streamlit logs
# Visible in console

# FastAPI logs
# Visible in console with timestamps
```

### Monitor API Usage
```bash
# OpenAI dashboard
https://platform.openai.com/account/usage/overview

# Pinecone console
https://console.pinecone.io/
```

## Deployment Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Add OpenAI API key to `.env`
- [ ] Add Pinecone credentials to `.env`
- [ ] Test with sample document
- [ ] Set `LOG_LEVEL=INFO` in production
- [ ] Enable CORS for specific domains
- [ ] Set rate limits
- [ ] Configure monitoring/alerts
- [ ] Test error handling
- [ ] Document API changes
- [ ] Plan for scaling

## Resources

### Official Docs
- OpenAI: https://platform.openai.com/docs
- Pinecone: https://docs.pinecone.io/
- FastAPI: https://fastapi.tiangolo.com/
- Streamlit: https://docs.streamlit.io/

### Guides
- README.md - Full feature documentation
- SETUP.md - Detailed installation guide
- MIGRATION.md - Upgrade from old system
- SUMMARY.md - What changed

### Support
- Check logs first: `LOG_LEVEL=DEBUG`
- Review SETUP.md troubleshooting section
- Check API status pages
- Verify environment configuration

## Common Tasks

### Update API Key
1. Get new key from service
2. Update `.env` file
3. Restart application

### Change Models
```env
# For better quality (but slower/more expensive)
OPENAI_LLM_MODEL=gpt-4

# For speed (but lower quality)
OPENAI_LLM_MODEL=gpt-3.5-turbo
```

### Reset Vector Store
```python
# In Pinecone console, delete index
# Code will recreate on next document upload
```

### View Stored Documents
```bash
# Stats endpoint shows chunk count
curl http://localhost:8000/api/v1/stats
```

---

**Last Updated:** January 2026
**Version:** 2.0.0 (OpenAI + Pinecone)
