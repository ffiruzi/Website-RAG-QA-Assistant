# Multi-stage Dockerfile - Runs both Frontend and Backend in one container
FROM node:18-alpine AS frontend-builder

# Build the React frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Main Python backend stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install crawler dependencies
COPY crawler/requirements.txt ./crawler_requirements.txt
RUN pip install --no-cache-dir -r crawler_requirements.txt

# Copy application code
COPY backend/ ./
COPY crawler/ ./crawler/

# Install crawler as editable package
RUN pip install -e ./crawler

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./static/

# Create necessary directories
RUN mkdir -p data logs alembic/versions

# Configure nginx to serve frontend and proxy API calls
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    \
    # Serve React frontend \
    location / { \
        root /app/static; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Proxy API calls to FastAPI backend \
    location /api/ { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    # Health check endpoint \
    location /health { \
        proxy_pass http://127.0.0.1:8000; \
    } \
    \
    # API docs \
    location /docs { \
        proxy_pass http://127.0.0.1:8000; \
    } \
    \
    location /openapi.json { \
        proxy_pass http://127.0.0.1:8000; \
    } \
}' > /etc/nginx/sites-available/default

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create startup script
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo "🚀 Starting Website RAG Q&A System..."' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Setup database if it does not exist' >> /app/start.sh && \
    echo 'if [ ! -f "app.db" ]; then' >> /app/start.sh && \
    echo '    echo "📊 Setting up database..."' >> /app/start.sh && \
    echo '    python simple_db_setup.py' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Start nginx in background' >> /app/start.sh && \
    echo 'echo "🌐 Starting nginx..."' >> /app/start.sh && \
    echo 'nginx' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Start FastAPI backend' >> /app/start.sh && \
    echo 'echo "⚡ Starting FastAPI backend..."' >> /app/start.sh && \
    echo 'exec python run_with_real.py' >> /app/start.sh && \
    chmod +x /app/start.sh



# Expose port 80 (nginx will handle both frontend and API proxying)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start everything
CMD ["/app/start.sh"]