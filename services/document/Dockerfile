# Document Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and Tesseract
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-hin \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared/ ./shared/

# Copy service code
COPY services/document/ ./services/document/

# Create directories
RUN mkdir -p logs storage

# Expose port
EXPOSE 8000

# Run service
CMD ["python", "-m", "services.document.main"]
