from io import BytesIO
from app.services.export.word_exporter import build_word_document


def test_build_word_document_structure():
    data = {
        "sections": [
            {"title": "Executive Summary", "content": "Summary content here."},
            {"title": "Technical Approach", "content": "Technical details here."},
        ]
    }
    doc = build_word_document(data)

    # Verify it can be saved without error
    buffer = BytesIO()
    doc.save(buffer)
    assert buffer.tell() > 0


def test_build_word_document_content():
    data = {
        "sections": [
            {"title": "Intro", "content": "Introduction paragraph."},
        ]
    }
    doc = build_word_document(data)

    texts = [p.text for p in doc.paragraphs]
    assert "Proposal" in texts
    assert "Intro" in texts
    assert "Introduction paragraph." in texts


def test_build_word_document_empty_sections():
    data = {"sections": []}
    doc = build_word_document(data)

    buffer = BytesIO()
    doc.save(buffer)
    assert buffer.tell() > 0

    texts = [p.text for p in doc.paragraphs]
    assert "Proposal" in texts
