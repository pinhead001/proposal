def build_analyze_prompt(texts):
    joined = "\n\n---\n\n".join(
        [f"PROPOSAL {i+1}:\n{t}" for i, t in enumerate(texts)]
    )
    return f"""You are an expert proposal analyst. Analyze the writing style across these past proposals.

{joined}

Provide a detailed analysis covering:
1. **Tone**: Formal vs conversational, confident vs cautious, technical vs accessible
2. **Structure patterns**: How sections are organized, use of headers, bullet points, paragraph length
3. **Technical depth**: Level of detail, use of jargon, specificity of solutions
4. **Persuasion techniques**: How value propositions are framed, use of evidence and metrics
5. **Voice**: First person vs third person, active vs passive, recurring phrases

Return a structured analysis that can be used to replicate this firm's writing style in future proposals."""
