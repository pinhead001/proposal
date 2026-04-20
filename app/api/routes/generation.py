import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.core.models import PipelineRequest, PipelineResponse
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
    return run_pipeline(payload.rfp_text, payload.proposal_texts)


@router.post("/stream-pipeline")
async def stream(payload: PipelineRequest):
    async def event_generator():
        try:
            async for event in stream_pipeline(payload.rfp_text, payload.proposal_texts):
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


@router.post("/save-proposal")
def save_proposal(payload: dict):
    rfp_text = payload.get("rfp_text", "")
    sections = payload.get("sections", [])
    entry_id = save_to_history(rfp_text, sections)
    return {"id": entry_id, "message": "Proposal saved to history"}


class RegenerateRequest(BaseModel):
    section_title: str = Field(..., min_length=1)
    rfp_text: str = Field(..., min_length=1)
    instructions: str = ""
    current_content: str = ""


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
