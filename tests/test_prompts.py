from app.services.llm.prompts.analyze import build_analyze_prompt
from app.services.llm.prompts.outline import build_outline_prompt
from app.services.llm.prompts.section import build_section_prompt


def test_build_analyze_prompt():
    result = build_analyze_prompt("Sample proposal text")
    assert "Sample proposal text" in result
    assert "Analyze writing style" in result


def test_build_outline_prompt():
    result = build_outline_prompt("RFP content", "analysis result")
    assert "RFP content" in result
    assert "analysis result" in result
    assert "Generate proposal outline" in result


def test_build_section_prompt():
    result = build_section_prompt("Executive Summary", "style info", "RFP data")
    assert "Executive Summary" in result
    assert "style info" in result
    assert "RFP data" in result
    assert "Write section" in result
