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

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 10000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
