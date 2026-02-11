# Voice Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared/ ./shared/

# Copy service code
COPY services/voice/ ./services/voice/

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run service
CMD ["python", "-m", "services.voice.main"]
