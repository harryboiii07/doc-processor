# Production-ready Dockerfile for Django Excel to JSON Conversion Service
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies required for Excel processing
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libmagic1 \
        libmagic-dev \
        curl \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p logs staticfiles \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app

# Switch to non-root user
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "sync", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "100", "--timeout", "300", "--keep-alive", "5", "--access-logfile", "-", "--error-logfile", "-", "excel_converter.wsgi:application"]
