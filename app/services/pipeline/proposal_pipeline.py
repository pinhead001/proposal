from app.services.llm.client import get_llm_client
from app.services.llm.prompts.analyze import build_analyze_prompt
from app.services.llm.prompts.outline import build_outline_prompt
from app.services.llm.prompts.section import build_section_prompt


def run_pipeline(rfp_text, proposal_texts):
    call_llm = get_llm_client()

    analysis = call_llm(build_analyze_prompt(proposal_texts))
    outline = call_llm(build_outline_prompt(rfp_text, analysis))

    sections = []

    for title in ["Executive Summary", "Technical Approach"]:
        content = call_llm(
            build_section_prompt(title, analysis, rfp_text)
        )
        sections.append({"title": title, "content": content})

    return {"sections": sections}
