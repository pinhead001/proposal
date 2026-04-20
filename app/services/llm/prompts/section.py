def build_section_prompt(section, analysis, rfp, outline="", prior_sections=None):
    prior_block = ""
    if prior_sections:
        summaries = []
        for ps in prior_sections:
            summary = ps["content"][:200] + "..." if len(ps["content"]) > 200 else ps["content"]
            summaries.append(f'- **{ps["title"]}**: {summary}')
        prior_block = f"\n## Previously Written Sections (maintain consistency):\n" + "\n".join(summaries) + "\n"

    outline_block = f"\n## Proposal Outline:\n{outline}\n" if outline else ""

    return f"""You are an expert proposal writer. Write the "{section}" section of a proposal.

## RFP Requirements:
{rfp}

## Firm Writing Style Analysis:
{analysis}
{outline_block}{prior_block}
## Instructions:
- Write the complete "{section}" section
- Match the firm's tone, structure, and technical depth from the style analysis
- Follow the proposal outline above for structure and key points
- Maintain consistency with previously written sections (don't repeat, do cross-reference)
- Address specific RFP requirements relevant to this section
- Use concrete details, metrics, and evidence where appropriate
- Write in a professional, client-ready tone
- Target 300-500 words for this section

Return only the section content, without the section title."""
