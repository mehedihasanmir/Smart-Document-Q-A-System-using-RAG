# Migration Guide: From Gemini to OpenAI & Pinecone

## Overview

This document details all changes made to upgrade the Smart Document Q&A System from Gemini to OpenAI and FAISS to Pinecone.

## Key Changes

### 1. **Configuration Module** (`config.py`)

#### Before (Gemini)
```python
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
GEMINI_API_URL = "https://generativelanguage.googleapis.com/..."
```

#### After (OpenAI + Pinecone)
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_LLM_MODEL = "gpt-4-turbo"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
```

### 2. **RAG Handler** (`rag_handler.py`)

#### Vector Database Changes

**Before (FAISS):**
```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Local FAISS index
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
```

**After (Pinecone):**
```python
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

# Cloud-based Pinecone index
index.upsert(vectors=[...])
results = index.query(vector=embedding, top_k=k)
```

#### Embedding Generation

**Before:**
```python
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = embedding_model.encode(chunks)
```

**After:**
```python
client = OpenAI(api_key=settings.OPENAI_API_KEY)
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=chunks
)
```

#### LLM Integration

**Before (Gemini API):**
```python
payload = {"contents": [{"parts": payload_parts}]}
response = session.post(GEMINI_API_URL, json=payload)
```

**After (OpenAI):**
```python
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[...],
    temperature=0.7,
    max_tokens=1000
)
```

### 3. **Advantages of New Architecture**

#### OpenAI Advantages
✅ Superior language models (GPT-4)
✅ Better multimodal support (vision)
✅ Consistent API across services
✅ Better documentation and support
✅ Industry-standard implementation

#### Pinecone Advantages
✅ Fully managed cloud service (no local storage)
✅ Serverless architecture
✅ Automatic scaling
✅ Better performance at scale
✅ Built-in metadata filtering
✅ Region availability options

### 4. **Dependencies Changed**

#### Removed
- `sentence-transformers`
- `faiss-cpu` (or `faiss-gpu`)
- Direct dependency on local file storage

#### Added
- `openai==1.12.0` - OpenAI API client (pinned for compatibility)
- `pinecone-client==3.0.0` - Pinecone vector DB client (pinned)
- `httpx==0.24.1` - HTTP client (pinned for OpenAI compatibility)

#### Version Pinning
The project now uses pinned versions to ensure compatibility:
- **openai 1.12.0**: Stable version with proper httpx support
- **httpx 0.24.1**: Compatible with OpenAI 1.12.0 (newer versions removed `proxies` parameter)
- **pinecone-client 3.0.0**: Stable serverless support

**Important:** Do not upgrade these packages independently. The versions are carefully selected to work together.

### 5. **Professional Code Enhancements**

#### Added Features
- ✅ Comprehensive logging with proper levels
- ✅ Type hints throughout codebase
- ✅ Detailed docstrings for all functions
- ✅ Professional error handling and validation
- ✅ Async/await for better concurrency
- ✅ Structured error responses
- ✅ Configuration validation on startup

#### Code Quality
```python
# Type hints
def add_document(self, text: str) -> int:
    """Process and add a document to the vector store."""

# Logging
logger.info(f"Processing document: {filename}")
logger.error(f"Error: {error_message}")

# Error handling
try:
    # operation
except APIError as e:
    logger.error(f"API error: {str(e)}")
    raise

# Validation
if not text or text.isspace():
    raise ValueError("Empty text provided")
```

### 6. **API Enhancements**

#### New FastAPI Endpoints
```
GET  /                      - Root/Welcome
GET  /health               - Health check
GET  /api/v1/stats         - Knowledge base statistics
POST /api/v1/upload        - Upload document
POST /api/v1/query         - Query documents
```

#### Enhanced Error Handling
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status": "error",
        "error": exc.detail,
        "status_code": exc.status_code
    }
```

### 7. **User Interface Improvements**

#### Streamlit Enhancements
- Better visual design with emoji icons
- Progress indicators
- Statistics dashboard
- Source document viewer
- Expandable context chunks
- Professional footer with links

#### Features Added
```python
# Metrics display
st.metric("Total Chunks", total_chunks)

# Expandable sections
with st.expander("📚 View Source Documents"):
    # Show source chunks

# Better error messages
st.error(f"❌ Error: {error_message}")
st.success(f"✅ Document processed")
```

### 8. **Configuration Files**

#### New Files Created
- `.env.example` - Template for environment variables
- `SETUP.md` - Comprehensive setup guide
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-service orchestration

#### Environment Variables
```env
OPENAI_API_KEY=...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-4-turbo
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
LOG_LEVEL=INFO
```

## Migration Steps

### For Existing Projects

1. **Backup old files:**
   ```bash
   git checkout -b backup-main
   git commit -am "Backup before migration"
   ```

2. **Update dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with API keys
   ```

4. **Test endpoints:**
   ```bash
   # Test health
   curl http://localhost:8000/health
   
   # Test upload
   curl -F "file=@test.pdf" http://localhost:8000/api/v1/upload
   
   # Test query
   curl -F "question=What is this?" http://localhost:8000/api/v1/query
   ```

5. **Clear old data:**
   ```bash
   # Pinecone handles vector storage
   # No local cleanup needed
   ```

## Performance Comparison

### Vector Storage

| Aspect | FAISS | Pinecone |
|--------|-------|----------|
| Storage | Local disk | Cloud |
| Scalability | Limited | Unlimited |
| Availability | Single machine | Replicated |
| Query speed | ~10ms | ~50ms |
| Cost | Free | Pay-per-use |

### Embedding Models

| Model | Dimension | Latency | Cost |
|-------|-----------|---------|------|
| all-MiniLM-L6-v2 | 384 | 50ms | Free |
| text-embedding-3-small | 1536 | 100ms | $0.02/1M |

### LLM Models

| Model | Quality | Speed | Cost |
|-------|---------|-------|------|
| Gemini 1.5 Flash | Good | Fast | ~$0.075/1M |
| GPT-4 Turbo | Excellent | Medium | ~$0.03/1K |

## Cost Estimation

### Monthly Usage (10,000 documents, 50,000 queries)

**OpenAI:**
- Embeddings: 10,000 docs × 1,536 tokens ≈ $0.30
- Queries: 50,000 × 2,000 tokens ≈ $3.00
- Total: ~$3.30

**Pinecone:**
- Serverless: ~$0.40 per hour average
- Monthly: ~$290 (with aggressive usage)
- Free tier: Up to 100,000 vector capacity

## Troubleshooting Migration

### "ModuleNotFoundError: No module named 'openai'"
```bash
pip install openai==1.12.0 httpx==0.24.1 pinecone-client==3.0.0
```

### "Client.__init__() got an unexpected keyword argument 'proxies'"
This is a version compatibility issue. Fix with:
```bash
# Uninstall conflicting versions
pip uninstall openai httpx -y

# Install compatible versions
pip install openai==1.12.0 httpx==0.24.1

# Verify
pip list | grep -E "openai|httpx"
```

**Why this happens:**
- OpenAI SDK changed how it handles HTTP clients
- Newer httpx versions (0.28+) removed the `proxies` parameter
- OpenAI 1.12.0 + httpx 0.24.1 is a stable combination

### "Pinecone index already exists"
```python
# The code handles this automatically
# Set PINECONE_INDEX_NAME to use existing index
```

### "OpenAI rate limit exceeded"
- Implement exponential backoff
- Use request queuing
- Upgrade API plan

### Performance degradation
- Check Pinecone query latency (can be 50-100ms)
- Consider caching embeddings locally
- Reduce TOP_K_RESULTS for faster responses

## Rollback Plan

If you need to revert to the previous version:

```bash
# Switch to backup branch
git checkout backup-main

# Reinstall old dependencies
pip install -r requirements.txt

# Reset environment
rm .env
# Use old environment variables
```

## Support & Resources

### Official Documentation
- OpenAI: https://platform.openai.com/docs
- Pinecone: https://docs.pinecone.io/

### Getting Help
- OpenAI Support: https://help.openai.com
- Pinecone Support: https://support.pinecone.io
- GitHub Issues: Create issue with migration tag

---

**Migration completed successfully!** 🎉
