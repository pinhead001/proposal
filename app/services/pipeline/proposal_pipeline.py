import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
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

_executor = ThreadPoolExecutor(max_workers=5)


def _call_llm_sync(prompt: str) -> str:
    call_llm = get_llm_client()
    return call_llm(prompt)


async def _call_llm_async(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _call_llm_sync, prompt)


def run_pipeline(rfp_text: str, proposal_texts: list[str] | None = None):
    call_llm = get_llm_client()

    texts = proposal_texts or load_proposals()
    if not texts:
        raise ValueError(
            "No proposal texts provided and none stored. "
            "Upload past proposals via /upload-proposals first."
        )

    analysis = load_analysis()
    if not analysis:
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


async def stream_pipeline(rfp_text: str, proposal_texts: list[str] | None = None):
    texts = proposal_texts or load_proposals()
    if not texts:
        raise ValueError(
            "No proposal texts provided and none stored. "
            "Upload past proposals via /upload-proposals first."
        )

    yield {"type": "progress", "percent": 5, "message": "Analyzing writing style..."}

    analysis = load_analysis()
    if analysis:
        logger.info("Using cached style analysis")
        yield {"type": "progress", "percent": 15, "message": "Using cached style analysis"}
    else:
        logger.info("Running style analysis on %d proposals", len(texts))
        analysis = await _call_llm_async(build_analyze_prompt(texts))
        save_analysis(analysis)

    yield {"type": "progress", "percent": 20, "message": "Generating outline..."}
    outline = await _call_llm_async(build_outline_prompt(rfp_text, analysis))

    yield {"type": "progress", "percent": 30, "message": "Generating sections in parallel..."}

    # Generate all sections in parallel
    section_tasks = []
    for title in DEFAULT_SECTIONS:
        prompt = build_section_prompt(title, analysis, rfp_text, outline)
        section_tasks.append((title, _call_llm_async(prompt)))

    tasks = [task for _, task in section_tasks]
    results = await asyncio.gather(*tasks)

    for i, (title, _) in enumerate(section_tasks):
        content = results[i]
        section = {"title": title, "content": content}
        pct = 30 + int(((i + 1) / len(DEFAULT_SECTIONS)) * 65)
        yield {"type": "progress", "percent": pct, "message": f"Completed: {title}"}
        yield {"type": "section", "data": section}

    yield {"type": "done"}


def regenerate_section(
    section_title: str,
    rfp_text: str,
    instructions: str = "",
    current_content: str = "",
) -> dict:
    call_llm = get_llm_client()

    analysis = load_analysis() or ""
    refinement = ""
    if instructions:
        refinement = f"\n## Refinement Instructions:\n{instructions}\n"
    if current_content:
        refinement += f"\n## Current Draft (improve this):\n{current_content}\n"

    prompt = build_section_prompt(section_title, analysis, rfp_text) + refinement

    content = call_llm(prompt)
    return {"title": section_title, "content": content}
