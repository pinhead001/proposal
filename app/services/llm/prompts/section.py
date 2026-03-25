def build_section_prompt(section, analysis, rfp):
    return f"""
Write section: {section}

RFP: {rfp}

Style: {analysis}
"""
