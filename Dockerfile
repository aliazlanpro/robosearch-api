# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY main.py .
COPY robosearch/ robosearch/

# Runtime configurations
ENV PYTHONPATH=/app
ENV TF_CPP_MIN_LOG_LEVEL=3
ENV PORT=8000

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["fastapi", "run", "main.py", "--port", "8000"]

## docker run -d --name mycontainer -p 8000:8000 robosearch-api