def build_outline_prompt(rfp, analysis):
    return f"""You are an expert proposal writer. Generate a detailed proposal outline responding to this RFP.

## RFP:
{rfp}

## Firm Writing Style Analysis:
{analysis}

Create an outline with the following sections:
1. Executive Summary
2. Technical Approach
3. Staffing Plan
4. Past Performance
5. Cost Narrative

For each section, provide:
- Key points to cover
- Specific RFP requirements addressed
- Recommended length (short/medium/long)

The outline should align with the firm's writing style identified above."""
