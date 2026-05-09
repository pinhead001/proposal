# Proposal AI

AI-powered proposal generation using Claude. Upload past proposals to learn your writing style, paste an RFP, and generate a complete proposal with a professional Word export.

## Features

- **Style Analysis** — learns tone, structure, and language patterns from your past proposals
- **5 Default Sections** — Executive Summary, Technical Approach, Staffing Plan, Past Performance, Cost Narrative
- **Customizable Sections** — select which sections to generate via the UI or API
- **Real-Time Streaming** — SSE progress updates as sections generate in parallel
- **Section Refinement** — regenerate any section with custom instructions
- **Inline Editing** — edit generated content directly in the browser
- **Copy to Clipboard** — one-click copy for any section
- **Proposal History** — save and reload past proposals
- **Word Export** — professional .docx with title page, TOC, styled headings, page breaks
- **File Upload** — drag-and-drop PDF/DOCX extraction
- **Provider Support** — Claude (default) or Azure OpenAI

## Prerequisites

- Python 3.11+
- [Anthropic API key](https://console.anthropic.com/)
- Docker (optional)

## Quick Start

```bash
git clone https://github.com/pinhead001/proposal.git
cd proposal
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
uvicorn app.main:app --reload
```

Open `http://localhost:8000` for the web UI, or `http://localhost:8000/docs` for the Swagger API docs.

## Docker

```bash
docker build -t proposal-ai .
docker run -p 8000:10000 -e ANTHROPIC_API_KEY=your_key proposal-ai
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key | Required |
| `LLM_PROVIDER` | `claude` or `azure` | `claude` |
| `LLM_MAX_TOKENS` | Max tokens per LLM call | `2048` |
| `LLM_TEMPERATURE` | Generation temperature | `0.3` |
| `PROPOSAL_API_KEY` | Optional API key to protect endpoints | None (no auth) |
| `CORS_ORIGINS` | Comma-separated allowed origins | `*` |
| `MAX_UPLOAD_SIZE_MB` | Max upload file size in MB | `10` |
| `MAX_RFP_LENGTH` | Max RFP text length in characters | `100000` |
| `PROPOSAL_DATA_DIR` | Directory for stored data | `data` |

### Azure OpenAI (optional)

| Variable | Description |
|---|---|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Azure endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name (default: `gpt-4o`) |
| `AZURE_OPENAI_API_VERSION` | API version (default: `2024-02-15-preview`) |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Web UI |
| `GET` | `/api/health` | Health check with provider info |
| `POST` | `/run-pipeline` | Generate proposal (sync) |
| `POST` | `/stream-pipeline` | Generate proposal (SSE streaming) |
| `POST` | `/upload-proposals` | Upload PDF/DOCX past proposals |
| `POST` | `/export` | Export sections to Word .docx |
| `POST` | `/regenerate-section` | Regenerate a single section with instructions |
| `POST` | `/save-proposal` | Save proposal to history |
| `GET` | `/history` | List saved proposals |
| `GET` | `/available-sections` | List default section titles |

### Example: Generate Proposal

```bash
curl -X POST http://localhost:8000/run-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "rfp_text": "We are seeking a vendor to build a cloud migration platform...",
    "proposal_texts": ["Past proposal 1...", "Past proposal 2..."],
    "sections": ["Executive Summary", "Technical Approach"]
  }'
```

### Example: Export to Word

```bash
curl -X POST http://localhost:8000/export \
  -H "Content-Type: application/json" \
  -d '{"sections": [{"title": "Summary", "content": "Our team will..."}]}' \
  --output proposal.docx
```

## Running Tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

All tests use mocked LLM calls — no API key required.

## Project Structure

```
proposal/
├── app/
│   ├── main.py                              # FastAPI app with middleware
│   ├── core/
│   │   ├── config.py                        # Environment-based configuration
│   │   ├── models.py                        # Pydantic request/response models
│   │   ├── auth.py                          # Optional API key authentication
│   │   └── middleware.py                    # Request ID + access logging
│   ├── api/routes/
│   │   ├── generation.py                    # Pipeline, regenerate, history routes
│   │   ├── export.py                        # Word document export
│   │   └── upload.py                        # File upload + text extraction
│   ├── services/
│   │   ├── llm/
│   │   │   ├── client.py                    # Provider factory (Claude/Azure)
│   │   │   ├── claude_client.py             # Claude with retry + lazy init
│   │   │   ├── azure_client.py              # Azure OpenAI with retry
│   │   │   └── prompts/                     # Prompt templates
│   │   ├── pipeline/
│   │   │   └── proposal_pipeline.py         # Sync, streaming, regenerate modes
│   │   ├── storage/
│   │   │   └── proposal_store.py            # JSON file storage
│   │   ├── extraction/
│   │   │   └── text_extractor.py            # PDF + DOCX text extraction
│   │   └── export/
│   │       └── word_exporter.py             # Professional Word doc builder
│   └── static/                              # Frontend (HTML/CSS/JS)
├── tests/                                   # 51 tests
├── Dockerfile                               # Multi-stage, non-root
├── requirements.txt
├── requirements-dev.txt
└── .github/workflows/deploy.yml             # CI: test → build → push
```

## Deployment

1. Push to `main` branch
2. GitHub Actions runs tests, then builds and pushes the Docker image
3. Pull the latest image on your server

Requires `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets in your GitHub repo settings.
