import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.core.models import ExportRequest
from app.services.export.word_exporter import build_word_document

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/export")
def export(payload: ExportRequest):
    try:
        doc = build_word_document(payload.sections)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
    except Exception as e:
        logger.exception("Export failed")
        raise HTTPException(status_code=500, detail="Failed to generate document")

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=proposal.docx"},
    )
