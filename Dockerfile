# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal requirements first (for better Docker layer caching)
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash agrimind
RUN chown -R agrimind:agrimind /app
USER agrimind

# Expose port
EXPOSE 8080

# Health check - removed curl dependency

# Run the cloud-optimized dashboard
CMD ["python", "agrimind_cloud_main.py"]
