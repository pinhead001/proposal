from io import BytesIO
from app.services.export.word_exporter import build_word_document


def test_build_word_document_structure():
    sections = [
        {"title": "Executive Summary", "content": "Summary content here."},
        {"title": "Technical Approach", "content": "Technical details here."},
    ]
    doc = build_word_document(sections)

    buffer = BytesIO()
    doc.save(buffer)
    assert buffer.tell() > 0


def test_build_word_document_content():
    sections = [
        {"title": "Intro", "content": "Introduction paragraph."},
    ]
    doc = build_word_document(sections)

    texts = [p.text for p in doc.paragraphs]
    assert "PROPOSAL" in texts
    assert "Intro" in texts
    assert "Introduction paragraph." in texts


def test_build_word_document_empty_sections():
    doc = build_word_document([])

    buffer = BytesIO()
    doc.save(buffer)
    assert buffer.tell() > 0

    texts = [p.text for p in doc.paragraphs]
    assert "PROPOSAL" in texts


def test_build_word_document_with_markdown_bullets():
    sections = [
        {"title": "Features", "content": "- Item one\n- Item two\n- Item three"},
    ]
    doc = build_word_document(sections)

    buffer = BytesIO()
    doc.save(buffer)
    assert buffer.tell() > 0
