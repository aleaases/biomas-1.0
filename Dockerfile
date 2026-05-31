# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libopenblas0 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app.py .
COPY requirements.txt .
COPY templates/ ./templates/
COPY yolov8n.pt .

# Create necessary directories
RUN mkdir -p outputs/excel outputs/pdf uploads

# Expose ports
# Port 5000 for local development
# Port 7860 for Hugging Face Spaces
EXPOSE 5000 7860

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/').read()" || exit 1

# Run the application
# Support both local development and Hugging Face Spaces
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --timeout 120 --workers 1 --threads 2"]

