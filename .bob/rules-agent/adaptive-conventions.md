# Adaptive Conventions & Self-Curating Rules

> Rule for dynamically learning and writing project-specific conventions during development.

## 1. When to Record a New Rule
When Bob in Agent mode discovers:
- A non-obvious architecture constraint (e.g. "use dataclass for all API DTOs")
- A platform or runtime quirk (e.g. "MPS requires float32, avoid double")
- A verified correction from the developer after a failed test

Bob is authorized to record the convention in `.bob/rules-agent/project-conventions.md`.

## 2. Strict Ponytail Guardrails (Prevent Context Bloat)
1. **One Single File**: Only write to `.bob/rules-agent/project-conventions.md`. Never create arbitrary new rule files.
2. **Hard Budget Limit**: The file MUST remain **≤ 200 tokens** at all times (approx. 10–12 concise bullet lines).
3. **No Redundancy**: Before writing, read existing bullets. If a new rule generalizes or supersedes an old one, replace it instead of appending.
4. **Binary Relevance**: Only record hard technical constraints, not general AI advice.

## 3. Format of `.bob/rules-agent/project-conventions.md`
```markdown
# Project Conventions (Learned)
- [Rule 1]: <one concise line specifying constraint and reason>
- [Rule 2]: <one concise line>
```
