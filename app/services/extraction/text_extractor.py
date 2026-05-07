import logging

logger = logging.getLogger(__name__)


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        return _extract_pdf(file_bytes)
    elif ext == "docx":
        return _extract_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Only PDF and DOCX are supported.")


def _extract_pdf(file_bytes: bytes) -> str:
    import pdfplumber
    from io import BytesIO

    text_parts = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    result = "\n\n".join(text_parts)
    if not result.strip():
        raise ValueError("PDF appears to be empty or image-only (no extractable text)")
    return result


def _extract_docx(file_bytes: bytes) -> str:
    from docx import Document
    from io import BytesIO

    doc = Document(BytesIO(file_bytes))
    text_parts = [p.text for p in doc.paragraphs if p.text.strip()]

    result = "\n\n".join(text_parts)
    if not result.strip():
        raise ValueError("DOCX appears to be empty (no extractable text)")
    return result
