## Code Standards & Review

Apply these standards when writing or modifying any Python code in this project.
When asked to "review" code, evaluate against these criteria and return a
structured findings report.

### 1. Structure & Modularity
- Functions do one thing and stay under ~40 lines
- Keep logic separate from I/O: functions that compute should not also read 
  files or call APIs — split them
- Extract reusable utilities rather than duplicating logic across scripts

### 2. Error Handling
- Wrap all file I/O, API calls, and subprocess calls in try/except
- Never use bare `except: pass` — always surface a meaningful error message
- Fail loudly during development; handle gracefully in production entry points

### 3. Maintainability
- No magic numbers or hardcoded paths — use named constants or a config object
- Variable and function names should read like plain English
- Comment *why*, not *what* — only where logic isn't self-evident

### 4. Python Idioms
- Use `pathlib` over `os.path`
- Prefer comprehensions over verbose loops where readability isn't sacrificed
- Use context managers (`with`) for file and resource handling
- Add type hints to all function signatures

### 5. Robustness
- Handle missing files, empty inputs, and malformed data explicitly
- Use `logging` instead of `print` in any script intended for reuse or 
  scheduled execution; `print` is acceptable in single-run utility scripts
- Never use mutable default arguments (e.g., `def f(x, data=[])`)

### Review Output Format
When asked to review code, respond with:

**Verdict:** PASS | NEEDS WORK | REFACTOR
- PASS — ready to deploy as-is
- NEEDS WORK — fixable in place, no structural changes required
- REFACTOR — structural issues require rethinking before proceeding

**Must Fix Before Deploy**
Bugs, silent failures, hardcoded secrets or paths, anything that will break
or expose data in production. Fix these before merging.

**Fix Soon**
Structural problems, missing error handling, non-idiomatic patterns that will
cause maintenance pain. Address in the next working session.

**Nice to Haves**
Naming improvements, docstrings, formatting, minor polish. Do if time permits.

List every finding in full. Do not summarize, truncate, or group findings to
save space.
