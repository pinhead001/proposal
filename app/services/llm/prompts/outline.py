def build_outline_prompt(rfp, analysis):
    return f"""
Generate proposal outline.

RFP: {rfp}

Style: {analysis}
"""
