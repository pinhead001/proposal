import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.core.config import MAX_UPLOAD_SIZE_MB
from app.core.models import UploadResponse
from app.services.extraction.text_extractor import extract_text
from app.services.storage.proposal_store import save_proposals, clear_analysis

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
MAX_FILES = 20


@router.post("/upload-proposals", response_model=UploadResponse)
async def upload_proposals(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_FILES} files allowed")

    extracted = []
    for f in files:
        content = await f.read()
        if len(content) > MAX_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"{f.filename} exceeds {MAX_UPLOAD_SIZE_MB}MB limit",
            )
        try:
            text = extract_text(content, f.filename)
            extracted.append(text)
            logger.info("Extracted %d chars from %s", len(text), f.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    save_proposals(extracted)
    clear_analysis()

    return UploadResponse(
        message=f"Successfully processed {len(extracted)} file(s)",
        file_count=len(extracted),
        extracted_texts=extracted,
    )
