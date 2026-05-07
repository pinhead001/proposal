from app.services.llm.prompts.analyze import build_analyze_prompt
from app.services.llm.prompts.outline import build_outline_prompt
from app.services.llm.prompts.section import build_section_prompt


def test_build_analyze_prompt():
    result = build_analyze_prompt(["Proposal A text", "Proposal B text"])
    assert "PROPOSAL 1" in result
    assert "PROPOSAL 2" in result
    assert "Proposal A text" in result
    assert "Analyze" in result or "analyze" in result


def test_build_analyze_prompt_single():
    result = build_analyze_prompt(["Single proposal"])
    assert "PROPOSAL 1" in result
    assert "Single proposal" in result


def test_build_outline_prompt():
    result = build_outline_prompt("RFP content", "analysis result")
    assert "RFP content" in result
    assert "analysis result" in result


def test_build_section_prompt_basic():
    result = build_section_prompt("Executive Summary", "style info", "RFP data")
    assert "Executive Summary" in result
    assert "style info" in result
    assert "RFP data" in result


def test_build_section_prompt_with_outline():
    result = build_section_prompt("Summary", "style", "rfp", outline="outline text")
    assert "outline text" in result


def test_build_section_prompt_with_prior_sections():
    prior = [{"title": "Intro", "content": "intro text"}]
    result = build_section_prompt("Summary", "style", "rfp", prior_sections=prior)
    assert "Intro" in result
    assert "intro text" in result
