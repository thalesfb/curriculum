# Commit Message Instructions

## Format

```
:emoji: type(scope): description
```

## Types

| Type | Emoji | When |
| ---- | ----- | ---- |
| `feat` | :sparkles: | New feature |
| `fix` | :bug: | Bug fix |
| `docs` | :books: | Documentation only |
| `style` | :art: | Formatting (no logic change) |
| `refactor` | :recycle: | Code restructuring |
| `test` | :white_check_mark: | Adding tests |
| `chore` | :wrench: | Maintenance (deps, configs) |
| `perf` | :zap: | Performance improvement |
| `ci` | :construction_worker: | CI/CD changes |
| `build` | :package: | Build system changes |

## Scopes

`i18n`, `hero`, `about`, `services`, `projects`, `contact`, `footer`, `header`, `figma`, `cv`, `deploy`, `docs`

## Examples

```
:sparkles: feat(i18n): add Spanish translations for contact section
:bug: fix(header): correct sticky positioning on mobile
:books: docs(adr): add ADR-0010 for form handling
:art: style(hero): adjust spacing between title and description
:recycle: refactor(projects): extract CarouselNav component
:wrench: chore(deps): update astro to 5.2.0
:zap: perf(images): convert PNGs to WebP
:construction_worker: ci(deploy): add health check step
```

## Rules

- Subject line max 72 characters
- Imperative mood ("add" not "added")
- No period at end
- Body optional, separated by blank line
