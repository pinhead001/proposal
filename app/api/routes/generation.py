import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.core.models import PipelineRequest, PipelineResponse, SectionResponse
from app.services.pipeline.proposal_pipeline import (
    run_pipeline,
    stream_pipeline,
    regenerate_section,
)
from app.services.storage.proposal_store import save_to_history, load_history

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/run-pipeline", response_model=PipelineResponse)
def run(payload: PipelineRequest):
    return run_pipeline(payload.rfp_text, payload.proposal_texts, payload.sections)


@router.get("/available-sections")
def available_sections():
    from app.services.pipeline.proposal_pipeline import DEFAULT_SECTIONS
    return {"sections": DEFAULT_SECTIONS}


@router.post("/stream-pipeline")
async def stream(payload: PipelineRequest):
    async def event_generator():
        try:
            async for event in stream_pipeline(payload.rfp_text, payload.proposal_texts, payload.sections):
                yield f"data: {json.dumps(event)}\n\n"
            yield "data: [DONE]\n\n"
        except ValueError as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        except Exception as e:
            logger.exception("Stream pipeline error")
            yield f"data: {json.dumps({'type': 'error', 'message': 'An unexpected error occurred'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history")
def get_history():
    return load_history()


class SaveProposalRequest(BaseModel):
    rfp_text: str = Field(..., min_length=1)
    sections: list[SectionResponse]


@router.post("/save-proposal")
def save_proposal(payload: SaveProposalRequest):
    entry_id = save_to_history(payload.rfp_text, [s.model_dump() for s in payload.sections])
    return {"id": entry_id, "message": "Proposal saved to history"}


class RegenerateRequest(BaseModel):
    section_title: str = Field(..., min_length=1, max_length=200)
    rfp_text: str = Field(..., min_length=1)
    instructions: str = Field("", max_length=5000)
    current_content: str = Field("", max_length=100000)


@router.post("/regenerate-section")
def regenerate(payload: RegenerateRequest):
    try:
        return regenerate_section(
            section_title=payload.section_title,
            rfp_text=payload.rfp_text,
            instructions=payload.instructions,
            current_content=payload.current_content,
        )
    except Exception as e:
        logger.exception("Regenerate section error")
        raise HTTPException(status_code=500, detail=str(e))
