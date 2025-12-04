# Backend Dockerfile for FastAPI + Celery
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and README for dependencies
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY backend/ .

# Create directories for uploads and outputs
RUN mkdir -p /app/uploads /app/outputs

# Expose port for FastAPI
EXPOSE 8000

# Default command (overridden in docker-compose.yml)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
