# --- Builder ---
FROM python:3.11-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Runtime ---
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app ./app

ENV PATH=/root/.local/bin:$PATH

EXPOSE 10000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
