# Orchestrator Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared/ ./shared/

# Copy service code
COPY services/orchestrator/ ./services/orchestrator/

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run service
CMD ["python", "-m", "services.orchestrator.main"]
