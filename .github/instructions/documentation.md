# Documentation Instructions

## When to update docs

- New feature added -> update relevant guide or create ADR
- Architecture decision changed -> create new ADR (don't edit accepted ones)
- New component -> update figma-design-system.md if design-related
- Config changed -> update DEVELOPMENT.md
- Deploy process changed -> update DEPLOYMENT.md

## ADR format

```markdown
# ADR-NNNN: Title

## Status
Proposed | Accepted | Deprecated | Superseded

## Date
YYYY-MM-DD

## Context
Why we needed to decide.

## Decision
What we decided.

## Consequences
### Positive
### Negative
```

## Rules

- ADRs are immutable once accepted. Create new ones to supersede.
- CHANGELOG.md updated on every release
- All docs in Portuguese (project language) unless technical terms
- No auto-generated docs without human review
- Keep docs concise: if it takes > 2 minutes to read, split it
