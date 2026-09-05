def build_section_prompt(
    section: str,
    analysis: str,
    rfp_text: str,
    outline: str = "",
    prior_sections: list[dict] | None = None,
) -> str:
    parts: list[str] = []
    if outline:
        parts.append(f"\n<proposal_outline>\n{outline}\n</proposal_outline>\n")
    if prior_sections:
        section_blocks = [
            f'\n<section title="{s["title"]}">\n{s["content"]}\n</section>'
            for s in prior_sections
        ]
        parts.append(
            "\n<previously_written_sections>"
            + "".join(section_blocks)
            + "\n</previously_written_sections>\n"
        )
    context = "".join(parts)

    return f"""You are an expert proposal writer. Write the "{section}" section of a government/business proposal.

<rfp_requirements>
{rfp_text}
</rfp_requirements>

<style_guide>
{analysis}
</style_guide>
{context}

Write the "{section}" section following these guidelines:
- Match the tone, voice, and style from the style guide
- Address relevant RFP requirements for this section
- Be specific and include concrete details where possible
- Use professional language appropriate for a formal proposal
- Ensure consistency with any previously written sections
- Aim for comprehensive coverage while remaining concise

Return only the section content, without the section title header."""
