# Semantic Versioning Instructions

## Format

```text
vMAJOR.MINOR.PATCH
```

| Part | When to bump | Example |
| ---- | ------------ | ------- |
| MAJOR | Breaking changes (cv.json schema, URL structure, i18n routing) | v1.0.0 -> v2.0.0 |
| MINOR | New features (new section, new language, new component) | v1.0.0 -> v1.1.0 |
| PATCH | Bug fixes, typos, style adjustments | v1.0.0 -> v1.0.1 |

## Automated Release Flow

Uses **semantic-release** or **release-please** to automate versioning based on conventional commits.

### How it works

```text
:sparkles: feat(i18n): add Spanish   ->  bumps MINOR  (v1.1.0)
:bug: fix(header): sticky overlap     ->  bumps PATCH  (v1.1.1)
:recycle: refactor(hero): extract comp ->  no bump (unless configured)
:books: docs(adr): add ADR-0010       ->  no bump
feat!: change cv.json schema           ->  bumps MAJOR  (v2.0.0)
```

The `!` after type or `BREAKING CHANGE:` in commit body triggers a MAJOR bump.

### GitHub Actions (release-please)

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          release-type: node
          changelog-types: >
            [
              {"type":"feat","section":"Features","hidden":false},
              {"type":"fix","section":"Bug Fixes","hidden":false},
              {"type":"perf","section":"Performance","hidden":false},
              {"type":"docs","section":"Documentation","hidden":false},
              {"type":"chore","section":"Maintenance","hidden":true}
            ]
```

### What release-please does automatically

1. Reads commit messages since last release
2. Determines version bump (MAJOR/MINOR/PATCH)
3. Updates `CHANGELOG.md` with grouped entries
4. Updates `package.json` version
5. Creates a Release PR
6. On merge: creates git tag + GitHub Release

### Manual release (if not using automation)

```bash
# Tag the release
git tag v1.0.0
git push origin v1.0.0

# Update CHANGELOG.md manually
# Update package.json version manually
```

## Rules

- NEVER manually edit version in `package.json` if using release-please
- NEVER manually create tags if using release-please
- Commit messages MUST follow conventional commits (see commit-messages.md)
- Breaking changes MUST use `!` suffix or `BREAKING CHANGE:` footer
- Pre-release versions: `v1.0.0-beta.1` for staging/preview
