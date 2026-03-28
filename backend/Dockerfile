# =============================================================================
# finance-copilot — backend/Dockerfile
# Multi-stage build: builder → development | production
# Non-root user, minimal runtime image.
# =============================================================================

# --------------- Stage 1: builder -------------------------------------------
# Installs all dependencies into a virtual env for clean copying
FROM python:3.11-slim AS builder

WORKDIR /build

# System build dependencies (needed to compile some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (layer caching)
COPY requirements.txt .

# Create a virtual environment and install into it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --------------- Stage 2: development ---------------------------------------
# Includes source code and dev tools; hot-reload via uvicorn --reload
FROM python:3.11-slim AS development

WORKDIR /app

# Install curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual env from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Source will be mounted as a volume in docker-compose for hot-reload
# Using root for development stage to avoid UID/GID permission issues with host mounts
EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--reload"]

# --------------- Stage 3: production ----------------------------------------
# Lean image; source code is baked in (no volume mounts in prod)
FROM python:3.11-slim AS production

WORKDIR /app

# System runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual env
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Bake in source
COPY backend/ ./backend/
COPY data/ ./data/

# Non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "backend.app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2"]
