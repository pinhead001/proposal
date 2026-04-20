import logging
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import generation, export, upload
from app.core.auth import verify_api_key
from app.core.config import LLM_PROVIDER, CORS_ORIGINS
from app.core.middleware import RequestIDMiddleware
from app.core.models import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="proposal-ai",
    version="0.2.0",
    dependencies=[Depends(verify_api_key)],
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation.router)
app.include_router(export.router)
app.include_router(upload.router)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/api/health", response_model=HealthResponse)
def health():
    return {"status": "running", "llm_provider": LLM_PROVIDER}


@app.get("/")
def root():
    return FileResponse(str(STATIC_DIR / "index.html"))
