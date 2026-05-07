def build_section_prompt(
    section: str,
    analysis: str,
    rfp_text: str,
    outline: str = "",
    prior_sections: list[dict] | None = None,
) -> str:
    context = ""
    if outline:
        context += f"\n## Proposal Outline:\n{outline}\n"
    if prior_sections:
        context += "\n## Previously Written Sections:\n"
        for s in prior_sections:
            context += f"\n### {s['title']}\n{s['content']}\n"

    return f"""You are an expert proposal writer. Write the "{section}" section of a government/business proposal.

## RFP Requirements:
{rfp_text}

## Writing Style Guide:
{analysis}
{context}

Write the "{section}" section following these guidelines:
- Match the tone, voice, and style from the style guide
- Address relevant RFP requirements for this section
- Be specific and include concrete details where possible
- Use professional language appropriate for a formal proposal
- Ensure consistency with any previously written sections
- Aim for comprehensive coverage while remaining concise

Return only the section content, without the section title header."""
