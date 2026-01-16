# Troubleshooting Guide

This guide covers common issues and their solutions for the Smart Document Q&A System.

---

## Installation Issues

### Issue: "Client.__init__() got an unexpected keyword argument 'proxies'"

**Symptoms:**
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```

**Cause:**
Version incompatibility between OpenAI SDK and httpx library. Newer httpx versions (0.28+) removed the `proxies` parameter that OpenAI 1.12.0 expects.

**Solution:**
```bash
# Windows
.\myenv\Scripts\python.exe -m pip install openai==1.12.0 httpx==0.24.1 pinecone-client==3.0.0 --force-reinstall

# macOS/Linux
python -m pip install openai==1.12.0 httpx==0.24.1 pinecone-client==3.0.0 --force-reinstall

# Verify installation
pip list | grep -E "openai|httpx|pinecone"

# Expected output:
# httpx                     0.24.1
# openai                    1.12.0
# pinecone-client           3.0.0
```

**Prevention:**
The `requirements.txt` file now includes pinned versions. Always install from requirements:
```bash
pip install -r requirements.txt
```

---

### Issue: "ModuleNotFoundError: No module named 'openai'"

**Cause:**
Dependencies not installed or virtual environment not activated.

**Solution:**
```bash
# Activate virtual environment
# Windows:
myenv\Scripts\activate

# macOS/Linux:
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Issue: "OPENAI_API_KEY is not set"

**Cause:**
Environment variables not configured or `.env` file missing.

**Solution:**
```bash
# 1. Check if .env file exists
ls -la .env  # macOS/Linux
dir .env     # Windows

# 2. If missing, create from template
cp .env.example .env  # macOS/Linux
copy .env.example .env  # Windows

# 3. Edit .env and add your API keys
# Use a text editor to add:
OPENAI_API_KEY=sk-proj-your-key-here
PINECONE_API_KEY=pcsk_your-key-here
PINECONE_ENVIRONMENT=us-east-1-aws

# 4. Verify the file
cat .env | grep API_KEY  # macOS/Linux
type .env | findstr API_KEY  # Windows

# 5. Restart your application
```

---

## Runtime Issues

### Issue: "Pinecone connection failed"

**Symptoms:**
```
Error initializing Pinecone index
Connection timeout
```

**Solutions:**

1. **Verify API Key:**
```bash
# Check your .env file
cat .env | grep PINECONE_API_KEY
```

2. **Check Environment Setting:**
```env
# In .env, ensure environment matches your Pinecone console
PINECONE_ENVIRONMENT=us-east-1-aws  # or your region
```

3. **Verify Internet Connection:**
```bash
# Test connectivity
ping api.pinecone.io
```

4. **Check Pinecone Status:**
Visit https://status.pinecone.io/

5. **Create Index Manually:**
- Go to Pinecone console
- Create index with:
  - Name: `smart-rag` (or your PINECONE_INDEX_NAME)
  - Dimensions: 1536
  - Metric: cosine
  - Cloud: AWS
  - Region: us-east-1

---

### Issue: "OpenAI rate limit exceeded"

**Symptoms:**
```
RateLimitError: Rate limit reached
```

**Solutions:**

1. **Check Usage:**
- Visit https://platform.openai.com/account/usage
- Review your current usage and limits

2. **Upgrade Plan:**
- Go to https://platform.openai.com/account/billing
- Add payment method or upgrade tier

3. **Implement Retry Logic:**
Already built into the code, but you can adjust settings:
```env
# Reduce concurrent requests
TOP_K_RESULTS=3  # Instead of 5
```

4. **Wait and Retry:**
Rate limits reset after a period (usually 1 minute)

---

### Issue: "Tesseract not found" (OCR for images)

**Symptoms:**
```
TesseractNotFoundError: tesseract is not installed
```

**Solutions:**

**Windows:**
```bash
# Using Chocolatey
choco install tesseract

# Or download installer from:
# https://github.com/UB-Mannheim/tesseract/wiki

# Add to PATH if needed:
# C:\Program Files\Tesseract-OCR
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Verify Installation:**
```bash
tesseract --version
```

---

### Issue: Port already in use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**

**For Streamlit (port 8501):**
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill existing process
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8501 | xargs kill -9
```

**For FastAPI (port 8000):**
```bash
# Use different port
python -m uvicorn main:app --port 8001

# Or kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

---

## Performance Issues

### Issue: Slow document processing

**Symptoms:**
- Document upload takes too long
- Application becomes unresponsive

**Solutions:**

1. **Reduce Chunk Size:**
```env
# In .env
CHUNK_SIZE=500  # Instead of 1000
CHUNK_OVERLAP=100  # Instead of 200
```

2. **Process Smaller Documents:**
- Split large PDFs into smaller files
- Extract only relevant pages

3. **Check System Resources:**
```bash
# Monitor CPU and memory
# Windows: Task Manager
# macOS: Activity Monitor
# Linux: htop or top
```

---

### Issue: Memory errors with large documents

**Symptoms:**
```
MemoryError
Out of memory
```

**Solutions:**

1. **Reduce Chunk Size:**
```env
CHUNK_SIZE=500
TOP_K_RESULTS=3
```

2. **Process Documents in Batches:**
Upload documents one at a time instead of bulk upload

3. **Increase System Memory:**
Close other applications or upgrade RAM

---

## API Issues

### Issue: "Invalid API key"

**Symptoms:**
```
AuthenticationError: Invalid API key
```

**Solutions:**

1. **Verify Key Format:**
```env
# OpenAI keys start with: sk-proj-
OPENAI_API_KEY=sk-proj-...

# Pinecone keys start with: pcsk_
PINECONE_API_KEY=pcsk_...
```

2. **Check for Extra Spaces:**
```bash
# Remove any trailing spaces or quotes
OPENAI_API_KEY=sk-proj-abc123  # Correct
OPENAI_API_KEY="sk-proj-abc123"  # Wrong (remove quotes)
OPENAI_API_KEY=sk-proj-abc123   # Wrong (trailing space)
```

3. **Regenerate Key:**
- OpenAI: https://platform.openai.com/api-keys
- Pinecone: https://console.pinecone.io/

---

### Issue: API requests timing out

**Symptoms:**
```
TimeoutError
Connection timeout
```

**Solutions:**

1. **Check Internet Connection:**
```bash
ping api.openai.com
ping api.pinecone.io
```

2. **Check Firewall/Proxy:**
- Ensure outbound HTTPS (443) is allowed
- Configure proxy if needed

3. **Increase Timeout:**
The code has reasonable timeouts, but check your network

---

## Docker Issues

### Issue: Docker container fails to start

**Solutions:**

1. **Check .env File:**
```bash
# Ensure .env exists in project root
ls -la .env
```

2. **Rebuild Container:**
```bash
docker-compose down
docker-compose up --build
```

3. **Check Logs:**
```bash
docker-compose logs
```

4. **Verify Ports:**
```bash
# Ensure ports 8501 and 8000 are free
netstat -an | grep -E "8501|8000"
```

---

## Data Issues

### Issue: "No documents processed yet"

**Symptoms:**
```
No documents processed yet. Please upload a document first.
```

**Solutions:**

1. **Upload a Document:**
- Use the Streamlit interface to upload a file
- Or use the API: `POST /api/v1/upload`

2. **Check Upload Success:**
- Look for success message
- Check logs for errors

3. **Verify File Format:**
Supported formats: PDF, DOCX, TXT, PNG, JPG, CSV, SQLite

---

### Issue: "No relevant information found"

**Symptoms:**
Answer says information not available in documents

**Solutions:**

1. **Rephrase Question:**
Try asking in different ways

2. **Increase Results:**
```env
TOP_K_RESULTS=10  # Instead of 5
```

3. **Check Document Content:**
Ensure the document actually contains relevant information

4. **Adjust Chunk Size:**
```env
CHUNK_SIZE=1500  # Larger chunks = more context
```

---

## Debugging Tips

### Enable Debug Logging

```env
# In .env
LOG_LEVEL=DEBUG
```

Then check console output for detailed information.

### Test Individual Components

**Test OpenAI Connection:**
```python
from openai import OpenAI
client = OpenAI(api_key="your-key")
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="test"
)
print(response)
```

**Test Pinecone Connection:**
```python
from pinecone import Pinecone
pc = Pinecone(api_key="your-key")
print(pc.list_indexes())
```

### Check Version Compatibility

```bash
# List installed versions
pip list | grep -E "openai|httpx|pinecone|streamlit|fastapi"

# Expected versions:
# openai        1.12.0
# httpx         0.24.1
# pinecone-client  3.0.0
```

---

## Getting Help

### Before Asking for Help

1. **Check Logs:**
   - Set `LOG_LEVEL=DEBUG`
   - Review console output

2. **Verify Configuration:**
   - Check `.env` file
   - Verify API keys are valid

3. **Test Connectivity:**
   - Ping OpenAI and Pinecone APIs
   - Check firewall settings

4. **Review Documentation:**
   - README.md
   - SETUP.md
   - This file

### Where to Get Help

1. **Official Documentation:**
   - OpenAI: https://platform.openai.com/docs
   - Pinecone: https://docs.pinecone.io/
   - FastAPI: https://fastapi.tiangolo.com/
   - Streamlit: https://docs.streamlit.io/

2. **Community Support:**
   - OpenAI Community: https://community.openai.com/
   - Pinecone Community: https://community.pinecone.io/
   - Stack Overflow: Tag with `openai`, `pinecone`

3. **Status Pages:**
   - OpenAI: https://status.openai.com/
   - Pinecone: https://status.pinecone.io/

---

## Quick Fixes Checklist

When something goes wrong, try these in order:

- [ ] Restart the application
- [ ] Check `.env` file exists and has correct keys
- [ ] Verify internet connection
- [ ] Check API service status pages
- [ ] Review logs with `LOG_LEVEL=DEBUG`
- [ ] Verify package versions: `pip list | grep -E "openai|httpx|pinecone"`
- [ ] Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- [ ] Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`
- [ ] Restart virtual environment
- [ ] Check system resources (CPU, memory, disk)

---

**Last Updated:** January 2026  
**Version:** 2.0.0 (OpenAI + Pinecone)

For additional help, refer to SETUP.md or README.md.
