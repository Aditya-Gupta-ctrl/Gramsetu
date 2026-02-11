# Agent Service Dockerfile
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy shared utilities
COPY shared/ ./shared/

# Copy service code
COPY services/agent/ ./services/agent/

# Create directories
RUN mkdir -p logs browser-data

# Expose port
EXPOSE 8000

# Run service
CMD ["python", "-m", "services.agent.main"]
