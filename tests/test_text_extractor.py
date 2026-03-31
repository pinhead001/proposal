import pytest
from io import BytesIO
from docx import Document
from app.services.extraction.text_extractor import (
    extract_text,
    extract_text_from_docx,
)


def _make_docx(paragraphs: list[str]) -> bytes:
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_extract_text_from_docx():
    content = _make_docx(["Hello world", "Second paragraph"])
    result = extract_text_from_docx(content)
    assert "Hello world" in result
    assert "Second paragraph" in result


def test_extract_text_dispatches_docx():
    content = _make_docx(["Test content"])
    result = extract_text("proposal.docx", content)
    assert "Test content" in result


def test_extract_text_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text("file.txt", b"some text")


def test_extract_text_case_insensitive():
    content = _make_docx(["Case test"])
    result = extract_text("FILE.DOCX", content)
    assert "Case test" in result
