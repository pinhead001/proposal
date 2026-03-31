import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import MAX_UPLOAD_SIZE_MB
from app.core.models import UploadResponse
from app.services.extraction.text_extractor import extract_text
from app.services.storage.proposal_store import save_proposals, clear_analysis

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_UPLOAD_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.post("/upload-proposals", response_model=UploadResponse)
async def upload_proposals(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    extracted_texts = []
    for file in files:
        if not file.filename:
            raise HTTPException(status_code=400, detail="File has no filename")

        content = await file.read()
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File '{file.filename}' exceeds {MAX_UPLOAD_SIZE_MB}MB limit",
            )

        try:
            text = extract_text(file.filename, content)
            extracted_texts.append(text)
            logger.info("Extracted text from %s (%d chars)", file.filename, len(text))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    save_proposals(extracted_texts)
    clear_analysis()

    return UploadResponse(
        message="Proposals uploaded and processed successfully",
        file_count=len(extracted_texts),
        extracted_texts=extracted_texts,
    )
