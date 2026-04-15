# Multi-stage Dockerfile for high-performance agent-recruiter

# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir build && python -m build --wheel

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Application dependency requirements for parsing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/dist/*.whl .
RUN pip install --no-cache-dir *.whl[all] && rm *.whl

# Setup directories for persistent data and logs
RUN mkdir -p /data/resumes /data/shortlists

VOLUME ["/data"]

ENTRYPOINT ["agent-recruiter"]
CMD ["--help"]
