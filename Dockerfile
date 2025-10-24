# ============================================================================
# Multi-Stage Production Dockerfile - Optimized for Size & Performance
# ============================================================================
# Stage 1: Builder (includes dev dependencies for building)
FROM python:3.11-slim as builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Determine which requirements file to use
ARG BUILD_ENV=production
COPY requirements*.txt ./

# Install dependencies based on build environment
RUN if [ "$BUILD_ENV" = "development" ]; then \
        pip install --no-cache-dir --user -r requirements.txt; \
    else \
        pip install --no-cache-dir --user -r requirements-production.txt; \
    fi

# Stage 2: Runtime (minimal production image)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ARG BUILD_ENV=production

# Install only essential runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

# Copy application code
COPY sutra/ ./sutra/
COPY *.py ./
COPY pyproject.toml ./

# Install package without dependencies (already installed in builder)
RUN pip install -e . --no-deps

# Copy application code
COPY sutra/ ./sutra/
COPY *.py ./
COPY pyproject.toml ./

# Install the package in development mode
RUN pip install -e .

# Create required directories
RUN mkdir -p /app/cache /app/logs /app/uploads /app/outputs

# Models will be mounted from volume at /app/models
# No model downloading in this Dockerfile!

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the production application
CMD ["python", "-m", "uvicorn", "sutra.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]