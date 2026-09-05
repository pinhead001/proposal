import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import CORS_ORIGINS, LLM_PROVIDER
from app.core.auth import verify_api_key
from app.core.middleware import RequestIDMiddleware
from app.core.models import HealthResponse
from app.api.routes import generation, export
from app.api.routes.upload import router as upload_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

auth_dep = [Depends(verify_api_key)]


@asynccontextmanager
async def lifespan(app):
    yield
    from app.services.pipeline.proposal_pipeline import _executor
    _executor.shutdown(wait=False)


app = FastAPI(title="Proposal AI", version="2.0.0", lifespan=lifespan)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials="*" not in CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation.router, dependencies=auth_dep)
app.include_router(export.router, dependencies=auth_dep)
app.include_router(upload_router, dependencies=auth_dep)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", llm_provider=LLM_PROVIDER)


@app.get("/")
def root():
    return FileResponse("app/static/index.html")
