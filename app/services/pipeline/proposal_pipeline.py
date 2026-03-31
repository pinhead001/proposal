import logging
from app.services.llm.client import get_llm_client
from app.services.llm.prompts.analyze import build_analyze_prompt
from app.services.llm.prompts.outline import build_outline_prompt
from app.services.llm.prompts.section import build_section_prompt
from app.services.storage.proposal_store import (
    load_proposals,
    load_analysis,
    save_analysis,
)

logger = logging.getLogger(__name__)

DEFAULT_SECTIONS = [
    "Executive Summary",
    "Technical Approach",
    "Staffing Plan",
    "Past Performance",
    "Cost Narrative",
]


def run_pipeline(rfp_text: str, proposal_texts: list[str] | None = None):
    call_llm = get_llm_client()

    # Use provided proposals, fall back to stored ones
    texts = proposal_texts or load_proposals()
    if not texts:
        raise ValueError(
            "No proposal texts provided and none stored. "
            "Upload past proposals via /upload-proposals first."
        )

    # Use cached analysis if available, otherwise generate and cache
    analysis = load_analysis()
    if analysis:
        logger.info("Using cached style analysis")
    else:
        logger.info("Running style analysis on %d proposals", len(texts))
        analysis = call_llm(build_analyze_prompt(texts))
        save_analysis(analysis)

    logger.info("Generating proposal outline")
    outline = call_llm(build_outline_prompt(rfp_text, analysis))

    sections = []
    for title in DEFAULT_SECTIONS:
        logger.info("Generating section: %s", title)
        content = call_llm(build_section_prompt(title, analysis, rfp_text, outline))
        sections.append({"title": title, "content": content})

    return {"sections": sections}
