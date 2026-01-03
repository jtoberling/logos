# ================================
# Build stage for dependencies
# ================================
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for build
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies (production only)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ================================
# Runtime stage (final image)
# ================================
FROM python:3.12-slim AS runtime

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    iputils-ping \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r logos && useradd -r -g logos logos

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set environment variables for runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    # FastEmbed cache configuration
    FASTEMBED_CACHE_DIR=/app/cache/fastembed \
    TMPDIR=/app/cache/fastembed \
    # HuggingFace cache configuration
    HF_HOME=/home/logos/.cache/huggingface \
    HF_HUB_CACHE=/home/logos/.cache/huggingface/hub \
    # Disable telemetry
    HF_HUB_DISABLE_TELEMETRY=1

# Create directories with proper permissions
RUN mkdir -p /app/data /app/logs /app/docs /app/cache/fastembed && \
    chown -R logos:logos /app

# Create HuggingFace cache directory and FastEmbed cache directory
RUN mkdir -p /home/logos/.cache/huggingface /app/cache/fastembed /tmp/fastembed_cache && \
    chown -R logos:logos /home/logos/.cache /app/cache /tmp/fastembed_cache && \
    chmod 755 /tmp/fastembed_cache

# Set work directory
WORKDIR /app

# Copy source code and docs (single layer for better caching)
COPY --chown=logos:logos src/ ./src/
COPY --chown=logos:logos docs/ ./docs/
# Note: VERSION file is optional - Python code has fallback to hardcoded version

# Switch to non-root user
USER logos

# Expose MCP server port
EXPOSE 6335

# Health check - check if port is listening
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('127.0.0.1', 6335)); s.close()" || exit 1

# Start the MCP server
CMD ["python", "-m", "src.main"]