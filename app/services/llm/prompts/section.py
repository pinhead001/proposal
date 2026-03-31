def build_section_prompt(section, analysis, rfp, outline=""):
    outline_block = f"\n## Proposal Outline:\n{outline}\n" if outline else ""
    return f"""You are an expert proposal writer. Write the "{section}" section of a proposal.

## RFP Requirements:
{rfp}

## Firm Writing Style Analysis:
{analysis}
{outline_block}
## Instructions:
- Write the complete "{section}" section
- Match the firm's tone, structure, and technical depth from the style analysis
- Follow the proposal outline above for structure and key points
- Address specific RFP requirements relevant to this section
- Use concrete details, metrics, and evidence where appropriate
- Write in a professional, client-ready tone
- Target 300-500 words for this section

Return only the section content, without the section title."""
