import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import generation, export, upload
from app.core.auth import verify_api_key
from app.core.config import LLM_PROVIDER, CORS_ORIGINS
from app.core.models import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="proposal-ai",
    version="0.1.0",
    dependencies=[Depends(verify_api_key)],
)

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


@app.get("/", response_model=HealthResponse)
def root():
    return {"status": "running", "llm_provider": LLM_PROVIDER}
