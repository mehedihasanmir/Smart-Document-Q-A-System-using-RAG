FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports for Streamlit and FastAPI
EXPOSE 8501 8000

# Set environment variables
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run both services with a script
RUN echo '#!/bin/bash\necho "Starting Smart Document Q&A System..."\necho "FastAPI running at http://0.0.0.0:8000"\necho "Streamlit running at http://0.0.0.0:8501"\necho "Open http://localhost:8501 in your browser"\npython -m uvicorn main:app --host 0.0.0.0 --port 8000 &\nstreamlit run app.py\n' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
