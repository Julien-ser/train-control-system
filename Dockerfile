# Train Control System Dockerfile
# Multi-stage build for smaller final image

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN groupadd -r traincontrol && useradd -r -g traincontrol traincontrol \
    && apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ src/
COPY tests/ tests/
COPY examples/ examples/
COPY setup.py .
COPY requirements.txt .

# Install package in development mode
RUN pip install --no-cache-dir -e .

# Switch to non-root user
USER traincontrol

# Health check - run tests to verify installation
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -m pytest tests/ -v --tb=short || exit 1

# Default command - run basic simulation
CMD ["python", "examples/basic_simulation.py"]
