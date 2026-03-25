def build_analyze_prompt(texts):
    return f"""
Analyze writing style across these proposals:

{texts}

Return tone, structure patterns, and technical depth.
"""
