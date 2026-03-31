from io import BytesIO
from unittest.mock import patch
from docx import Document
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _make_docx_bytes(text: str) -> bytes:
    doc = Document()
    doc.add_paragraph(text)
    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


@patch("app.api.routes.upload.save_proposals")
@patch("app.api.routes.upload.clear_analysis")
def test_upload_docx_files(mock_clear, mock_save):
    file1 = _make_docx_bytes("Past proposal one")
    file2 = _make_docx_bytes("Past proposal two")

    response = client.post(
        "/upload-proposals",
        files=[
            ("files", ("prop1.docx", BytesIO(file1), "application/octet-stream")),
            ("files", ("prop2.docx", BytesIO(file2), "application/octet-stream")),
        ],
    )

    assert response.status_code == 200
    data = response.json()
    assert data["file_count"] == 2
    assert "Past proposal one" in data["extracted_texts"][0]
    assert "Past proposal two" in data["extracted_texts"][1]
    mock_save.assert_called_once()
    mock_clear.assert_called_once()


def test_upload_unsupported_file():
    response = client.post(
        "/upload-proposals",
        files=[
            ("files", ("notes.txt", BytesIO(b"text content"), "text/plain")),
        ],
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
