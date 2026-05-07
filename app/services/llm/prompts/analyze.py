def build_analyze_prompt(texts: list[str]) -> str:
    enumerated = ""
    for i, text in enumerate(texts, 1):
        enumerated += f"\n--- PROPOSAL {i} ---\n{text}\n"

    return f"""You are an expert proposal analyst. Analyze the writing style across these past proposals and extract patterns that should be replicated in future proposals.

{enumerated}

Provide a structured analysis covering:
1. **Tone & Voice**: Formal/informal, active/passive, confidence level
2. **Structure Patterns**: How sections are organized, use of headers/bullets/paragraphs
3. **Technical Depth**: Level of detail, use of jargon, specificity
4. **Persuasion Techniques**: How value propositions are framed, use of evidence
5. **Language Patterns**: Common phrases, transition words, sentence complexity

Return your analysis as a structured document that can guide future proposal writing."""
