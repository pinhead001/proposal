# Quickstart: Running proposal-ai with Docker in VS Code

## 1. Install Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — install and make sure it's running
- [VS Code](https://code.visualstudio.com/)
- VS Code extension: **Docker** (by Microsoft) — install from the Extensions sidebar (`Ctrl+Shift+X`, search "Docker")

## 2. Open the Project

Open VS Code, then:

```
File → Open Folder → select the proposal/ directory
```

Or from terminal:

```bash
code proposal/
```

## 3. Create a `.env` File

In the project root, create a `.env` file:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

> This file is already in `.dockerignore` and `.gitignore` so it won't be committed or included in the image.

## 4. Build the Docker Image

Open the VS Code integrated terminal (`` Ctrl+` ``) and run:

```bash
docker build -t proposal-ai .
```

Or right-click the `Dockerfile` in the Explorer sidebar and select **Build Image...**, then enter `proposal-ai:latest` as the tag.

## 5. Run the Container

From the terminal:

```bash
docker run -p 8000:10000 --env-file .env proposal-ai
```

Or using the Docker extension sidebar:

1. Click the **Docker** icon in the left Activity Bar
2. Under **Images**, find `proposal-ai`
3. Right-click → **Run**
4. Configure port mapping `8000:10000` and environment variables when prompted

## 6. Verify It's Running

Open a browser or use the terminal:

```bash
curl http://localhost:8000/
```

Expected response:

```json
{"status": "running"}
```

Or open the Swagger UI directly:

```
http://localhost:8000/docs
```

## 7. Test the API

### Generate a proposal

```bash
curl -X POST http://localhost:8000/run-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "rfp_text": "We need a cloud migration platform...",
    "proposal_texts": ["Past proposal text here..."]
  }'
```

### Export to Word

```bash
curl -X POST http://localhost:8000/export \
  -H "Content-Type: application/json" \
  -d '{
    "sections": [
      {"title": "Executive Summary", "content": "Our approach..."},
      {"title": "Technical Approach", "content": "We will use..."}
    ]
  }' \
  --output proposal.docx
```

## 8. View Logs

In the Docker extension sidebar, right-click the running container → **View Logs** to see application output in the VS Code terminal.

## 9. Stop the Container

From terminal:

```bash
docker ps
docker stop <container_id>
```

Or in the Docker extension sidebar, right-click the running container → **Stop**.

## Troubleshooting

| Issue | Fix |
|---|---|
| `docker: command not found` | Make sure Docker Desktop is installed and running |
| Port 8000 already in use | Change to another port: `docker run -p 9000:10000 --env-file .env proposal-ai` |
| `ANTHROPIC_API_KEY` errors | Verify your `.env` file exists and the key is valid |
| Container exits immediately | Run `docker logs <container_id>` to check for errors |
