from fastapi import APIRouter
from app.services.pipeline.proposal_pipeline import run_pipeline

router = APIRouter()


@router.post("/run-pipeline")
def run(payload: dict):
    return run_pipeline(payload["rfp_text"], payload["proposal_texts"])
