from app.services.llm.claude_client import call_claude
from app.services.llm.prompts.analyze import build_analyze_prompt
from app.services.llm.prompts.outline import build_outline_prompt
from app.services.llm.prompts.section import build_section_prompt


def run_pipeline(rfp_text, proposal_texts):
    analysis = call_claude(build_analyze_prompt(proposal_texts))
    outline = call_claude(build_outline_prompt(rfp_text, analysis))

    sections = []

    for title in ["Executive Summary", "Technical Approach"]:
        content = call_claude(
            build_section_prompt(title, analysis, rfp_text)
        )
        sections.append({"title": title, "content": content})

    return {"sections": sections}
