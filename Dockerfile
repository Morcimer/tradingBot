# Use a slim Python image
FROM python:3.14-slim

# Set working dir
WORKDIR /app

# Install system deps required by some Python packages (build tools, SSL, tzdata)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      libpq-dev \
      libssl-dev \
      ca-certificates \
      tzdata \
      git && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/requirements.txt

# Install Python deps
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Create non-root user and fix permissions
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (if using API / dashboard)
EXPOSE 8000

# Default command: run the bot script or FastAPI app
# Replace `main:app` with your ASGI app object or `bot.py` for script mode
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop"]
