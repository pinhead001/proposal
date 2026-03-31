from fastapi import APIRouter
from app.core.models import PipelineRequest, PipelineResponse
from app.services.pipeline.proposal_pipeline import run_pipeline

router = APIRouter()


@router.post("/run-pipeline", response_model=PipelineResponse)
def run(payload: PipelineRequest):
    return run_pipeline(payload.rfp_text, payload.proposal_texts)
