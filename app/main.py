import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import generation, export, upload
from app.core.config import LLM_PROVIDER
from app.core.models import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(title="proposal-ai", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation.router)
app.include_router(export.router)
app.include_router(upload.router)


@app.get("/", response_model=HealthResponse)
def root():
    return {"status": "running", "llm_provider": LLM_PROVIDER}
