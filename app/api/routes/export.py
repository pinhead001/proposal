from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.services.export.word_exporter import build_word_document

router = APIRouter()


@router.post("/export")
def export(payload: dict):
    doc = build_word_document(payload)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=proposal.docx"},
    )
