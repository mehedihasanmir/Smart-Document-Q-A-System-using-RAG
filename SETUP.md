# Smart Document Q&A System - Setup Guide

This guide walks you through setting up and running the Smart Document Q&A System with OpenAI and Pinecone.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [API Key Setup](#api-key-setup)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- Python 3.8 or higher
- pip package manager
- 2GB+ free disk space
- Internet connection

### Software to Install
- **OpenAI Account**: [Create at OpenAI](https://openai.com/api/)
- **Pinecone Account**: [Create at Pinecone](https://www.pinecone.io/)
- **Tesseract OCR** (for image text extraction):
  - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - **Mac**: `brew install tesseract`
  - **Linux**: `sudo apt-get install tesseract-ocr`

## API Key Setup

### 1. OpenAI API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy and save the key securely
4. Set a usage limit in billing settings

**Models Used:**
- Embeddings: `text-embedding-3-small` (~$0.02 per 1M tokens)
- LLM: `gpt-4-turbo` (~$0.03/$0.06 per 1K tokens)

### 2. Pinecone API Key

1. Go to [Pinecone Console](https://console.pinecone.io/)
2. Create a new project
3. Get your API key and environment from the dashboard
4. Note the environment (e.g., `us-east-1-aws`)

**Serverless Configuration:**
- Cloud: AWS
- Region: us-east-1
- Metric: Cosine

## Installation

### Step 1: Clone Repository
```bash
cd Smart-Document-Q-A-System-using-RAG
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv myvenv
myvenv\Scripts\activate

# macOS/Linux
python3 -m venv myvenv
source myvenv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Important:** The project uses specific versions of OpenAI and httpx libraries for compatibility:
- `openai==1.12.0`
- `httpx==0.24.1`
- `pinecone-client==3.0.0`

These versions are pinned to avoid the `proxies` parameter error. If you encounter version conflicts, run:
```bash
pip install openai==1.12.0 httpx==0.24.1 pinecone-client==3.0.0 --force-reinstall
```

## Configuration

### Step 1: Create .env File
```bash
cp .env.example .env
```

### Step 2: Edit .env File
Open `.env` and fill in your API keys and configuration:

```env
# ===== OPENAI CONFIGURATION =====
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-4-turbo

# ===== PINECONE CONFIGURATION =====
PINECONE_API_KEY=pcsk_xxxxxxxxxxxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=smart-rag

# ===== RAG CONFIGURATION =====
CHUNK_SIZE=1000          # Size of text chunks
CHUNK_OVERLAP=200        # Overlap between chunks
TOP_K_RESULTS=5          # Number of results to retrieve

# ===== LOGGING CONFIGURATION =====
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Running the Application

### Option 1: Streamlit Web Interface (Recommended for Users)

```bash
streamlit run app.py
```

**Expected Output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Option 2: FastAPI REST API (Recommended for Developers)

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Option 3: Docker Compose

```bash
# Create .env file first
cp .env.example .env
# Edit .env with your credentials

# Start both services
docker-compose up --build

# Services will be available at:
# Streamlit: http://localhost:8501
# FastAPI: http://localhost:8000
```

## Testing

### Test Streamlit Interface

1. Open http://localhost:8501
2. Upload a test PDF or document
3. Ask a question about the document
4. Check the answer and source chunks

### Test FastAPI

#### Upload a Document
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "accept: application/json" \
  -F "file=@your_document.pdf"
```

#### Query Documents
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "accept: application/json" \
  -F "question=What is the main topic?"
```

#### Check Health
```bash
curl http://localhost:8000/health
```

#### Get Statistics
```bash
curl http://localhost:8000/api/v1/stats
```

## Troubleshooting

### Issue: "OPENAI_API_KEY is not set"

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check key is set
grep OPENAI_API_KEY .env

# Reinstall python-dotenv
pip install --force-reinstall python-dotenv
```

### Issue: "Pinecone connection failed"

**Solutions:**
1. Verify API key in .env
2. Check internet connection
3. Verify environment setting matches Pinecone console
4. Try creating index manually in Pinecone console

### Issue: Tesseract OCR not found

**Windows:**
1. Download installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to default location: `C:\Program Files\Tesseract-OCR`
3. Add to PATH or update pytesseract in code

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Issue: Port 8501 or 8000 already in use

**Solution:**
```bash
# Streamlit on different port
streamlit run app.py --server.port 8502

# FastAPI on different port
python -m uvicorn main:app --port 8001
```

### Issue: Memory errors with large documents

**Solution:**
Reduce `CHUNK_SIZE` in .env:
```env
CHUNK_SIZE=500    # Smaller chunks use less memory
CHUNK_OVERLAP=100
```

### Issue: Rate limit errors from OpenAI

**Solution:**
1. Check OpenAI usage in dashboard
2. Upgrade API plan if needed
3. Implement request throttling
4. Reduce number of concurrent requests

### Issue: "Client.__init__() got an unexpected keyword argument 'proxies'"

**Cause:** Version incompatibility between OpenAI client and httpx library.

**Solution:**
```bash
# Install compatible versions
pip install openai==1.12.0 httpx==0.24.1 pinecone-client==3.0.0 --force-reinstall

# Verify installation
pip list | grep -E "openai|httpx|pinecone"

# Restart your application
streamlit run app.py
```

**Why this happens:**
- OpenAI 1.12.0 requires httpx 0.24.1
- Newer httpx versions (0.28+) removed the `proxies` parameter
- The pinned versions in `requirements.txt` prevent this issue

## Performance Tips

### Optimize Costs
```env
# Use cheaper embedding model
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Reduce API calls
TOP_K_RESULTS=3
CHUNK_SIZE=1500
```

### Optimize Speed
```env
# Smaller chunks = faster processing
CHUNK_SIZE=500
TOP_K_RESULTS=3

# Enable caching (future enhancement)
```

### Monitor Usage
```bash
# Check OpenAI usage
curl https://api.openai.com/v1/usage/tokens \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## Production Deployment

### Security Checklist
- [ ] Move API keys to secure secret management (AWS Secrets Manager, etc.)
- [ ] Enable HTTPS/TLS
- [ ] Set CORS properly for specific domains
- [ ] Add API authentication/rate limiting
- [ ] Enable audit logging
- [ ] Use environment-specific configuration

### Performance Checklist
- [ ] Use production ASGI server (Gunicorn, etc.)
- [ ] Enable caching for embeddings
- [ ] Use load balancing
- [ ] Monitor API usage and costs
- [ ] Set up alerting

### Deployment Example (AWS)
```bash
# Build Docker image
docker build -t smart-rag:latest .

# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com

docker tag smart-rag:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/smart-rag:latest

docker push \
  123456789.dkr.ecr.us-east-1.amazonaws.com/smart-rag:latest

# Deploy to ECS or EKS
# ...
```

## Getting Help

### Resources
- [OpenAI Documentation](https://platform.openai.com/docs)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Community
- OpenAI Forums: https://community.openai.com/
- Pinecone Community: https://community.pinecone.io/
- Stack Overflow: Tag with `openai` and `pinecone`

---

**Enjoy your Smart Document Q&A System!**
