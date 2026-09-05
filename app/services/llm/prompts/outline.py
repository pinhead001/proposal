def build_outline_prompt(rfp_text: str, analysis: str) -> str:
    return f"""You are an expert proposal strategist. Based on the RFP requirements and the writing style analysis from past winning proposals, generate a detailed proposal outline.

<rfp_requirements>
{rfp_text}
</rfp_requirements>

<style_analysis>
{analysis}
</style_analysis>

Create a comprehensive outline that:
1. Addresses every requirement mentioned in the RFP
2. Follows the structural patterns identified in the style analysis
3. Includes key talking points for each section
4. Notes where to emphasize differentiators and past performance
5. Suggests evidence or data points to include

Return the outline as a structured document with section headers and bullet points."""
