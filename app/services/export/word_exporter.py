from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT


def build_word_document(data):
    doc = Document()

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    style.paragraph_format.space_after = Pt(8)
    style.paragraph_format.line_spacing = 1.15

    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)

    # Title page
    for _ in range(6):
        doc.add_paragraph('')

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run('PROPOSAL')
    run.font.size = Pt(36)
    run.font.color.rgb = RGBColor(0x2D, 0x31, 0x48)
    run.bold = True

    doc.add_paragraph('')

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run('Prepared with Proposal AI')
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    doc.add_page_break()

    # Table of contents header
    toc_heading = doc.add_heading('Table of Contents', level=1)
    toc_heading.runs[0].font.color.rgb = RGBColor(0x2D, 0x31, 0x48)

    for i, section_data in enumerate(data["sections"], 1):
        toc_entry = doc.add_paragraph()
        run = toc_entry.add_run(f'{i}.  {section_data["title"]}')
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
        toc_entry.paragraph_format.space_after = Pt(4)

    doc.add_page_break()

    # Sections
    for i, section_data in enumerate(data["sections"]):
        heading = doc.add_heading(section_data["title"], level=1)
        heading.runs[0].font.color.rgb = RGBColor(0x2D, 0x31, 0x48)

        for paragraph_text in section_data["content"].split('\n\n'):
            paragraph_text = paragraph_text.strip()
            if not paragraph_text:
                continue
            p = doc.add_paragraph(paragraph_text)
            p.paragraph_format.space_after = Pt(8)

        if i < len(data["sections"]) - 1:
            doc.add_page_break()

    # Footer
    footer_section = doc.sections[-1]
    footer = footer_section.footer
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer_para.add_run('CONFIDENTIAL')
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    return doc
