from docx import Document


def build_word_document(data):
    doc = Document()
    doc.add_heading("Proposal", 0)

    for section in data["sections"]:
        doc.add_heading(section["title"], 1)
        doc.add_paragraph(section["content"])

    return doc
