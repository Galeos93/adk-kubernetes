# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app user and group
RUN groupadd -r app && useradd -r -g app app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Configure Poetry: Don't create virtual environment, install to system Python
RUN poetry config virtualenvs.create false

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies
RUN poetry install --only=main --no-dev

# Copy application code
COPY ./application ./application
COPY ./domain ./domain
COPY ./infrastructure ./infrastructure
COPY ./main.py .

# Create empty session_db.sqlite if it doesn't exist
RUN touch session_db.sqlite

# Create necessary directories and set permissions
RUN mkdir -p /app/logs && \
    chown -R app:app /app

# Switch to non-root user
USER app

# Expose port (matches config.yaml)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python", "main.py"]
