# proposal-ai

AI-powered proposal generation using Claude. Analyzes past proposals to learn your firm's voice and structure, then generates client-ready proposals from RFP inputs.

## Prerequisites

- Python 3.11+
- [Anthropic API key](https://console.anthropic.com/)
- Docker (optional)

## Setup

```bash
git clone https://github.com/pinhead001/proposal.git
cd proposal
pip install -r requirements.txt
```

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Yes |

```bash
export ANTHROPIC_API_KEY=your_key
```

## Running Locally

```bash
uvicorn app.main:app --reload
```

The app will be available at `http://localhost:8000`. Open `http://localhost:8000/docs` for the interactive Swagger UI.

## Running with Docker

```bash
docker build -t proposal-ai .
docker run -p 8000:10000 -e ANTHROPIC_API_KEY=your_key proposal-ai
```

The app will be available at `http://localhost:8000`.

## API Endpoints

### `GET /`

Health check.

```bash
curl http://localhost:8000/
```

Response:

```json
{"status": "running"}
```

### `POST /run-pipeline`

Generate proposal sections from an RFP and past proposals.

```bash
curl -X POST http://localhost:8000/run-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "rfp_text": "We are seeking a vendor to build a cloud migration platform...",
    "proposal_texts": [
      "Past proposal 1 text...",
      "Past proposal 2 text...",
      "Past proposal 3 text..."
    ]
  }'
```

Response:

```json
{
  "sections": [
    {"title": "Executive Summary", "content": "..."},
    {"title": "Technical Approach", "content": "..."}
  ]
}
```

### `POST /export`

Export proposal sections to a Word document (.docx).

```bash
curl -X POST http://localhost:8000/export \
  -H "Content-Type: application/json" \
  -d '{
    "sections": [
      {"title": "Executive Summary", "content": "Our team will..."},
      {"title": "Technical Approach", "content": "We propose using..."}
    ]
  }' \
  --output proposal.docx
```

## Running Tests

```bash
python -m pytest tests/ -v
```

All tests use mocked Claude calls — no API key required.

## Project Structure

```
proposal/
├── app/
│   ├── main.py                          # FastAPI app entrypoint
│   ├── api/routes/
│   │   ├── generation.py                # /run-pipeline endpoint
│   │   └── export.py                    # /export endpoint
│   ├── services/
│   │   ├── llm/
│   │   │   ├── claude_client.py         # Anthropic Claude client
│   │   │   └── prompts/
│   │   │       ├── analyze.py           # Style analysis prompt
│   │   │       ├── outline.py           # Outline generation prompt
│   │   │       └── section.py           # Section writing prompt
│   │   ├── pipeline/
│   │   │   └── proposal_pipeline.py     # Multi-step generation pipeline
│   │   └── export/
│   │       └── word_exporter.py         # Word document builder
│   └── core/
├── tests/
├── Dockerfile
├── requirements.txt
└── .github/workflows/deploy.yml
```

## Deployment

1. Push to `main` branch on GitHub
2. GitHub Actions builds and pushes the Docker image to Docker Hub
3. Pull the latest image on your server (e.g. Render, AWS, etc.)

Requires `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets configured in your GitHub repository settings.
