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
    assert "PROPOSAL" in texts
    assert "Introduction paragraph." in texts


def test_build_word_document_has_toc():
    data = {
        "sections": [
            {"title": "Section One", "content": "Content one."},
            {"title": "Section Two", "content": "Content two."},
        ]
    }
    doc = build_word_document(data)

    texts = [p.text for p in doc.paragraphs]
    assert any("Table of Contents" in t for t in texts)
    assert any("Section One" in t for t in texts)
    assert any("Section Two" in t for t in texts)


def test_build_word_document_has_footer():
    data = {"sections": [{"title": "Test", "content": "Content."}]}
    doc = build_word_document(data)

    footer_text = doc.sections[-1].footer.paragraphs[0].text
    assert "CONFIDENTIAL" in footer_text


def test_build_word_document_empty_sections():
    data = {"sections": []}
    doc = build_word_document(data)

    buffer = BytesIO()
    doc.save(buffer)
    assert buffer.tell() > 0
