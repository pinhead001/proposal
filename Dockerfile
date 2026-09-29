# --- Builder ---
FROM python:3.11-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Runtime ---
FROM python:3.11-slim

RUN useradd -m -r appuser
WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY app ./app

RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Uploaded proposals, cached style analysis, and generation history live here.
# Mount a host directory or named volume over it, or the data is lost when the
# container is replaced.
VOLUME ["/app/data"]

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 10000

# /api/health is deliberately exempt from API-key auth so this works whether or
# not PROPOSAL_API_KEY is set. urlopen raises on any non-2xx, failing the check.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:10000/api/health', timeout=4)" || exit 1

# Single worker is required: proposal_store serializes writes with an in-process
# threading.Lock, which does not hold across worker processes.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]
