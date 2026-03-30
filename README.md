# thales.optimizr.site

Portfolio profissional de **Thales Ferreira** — Full Stack Data Engineer | Python & ML | DevOps Specialist.

## Stack

| Layer | Technology |
| ----- | ---------- |
| Framework | Astro 5/6 |
| Styling | Tailwind CSS 4 |
| Interactivity | Vanilla JS (CSS-first) |
| i18n | PT / EN / ES (routing) |
| Data | JSON (single source of truth) |
| Deploy | VPS + NGINX + GitHub Actions |
| Design | Figma (variables, components, dark mode) |

## Quick Start

```bash
git clone <repo-url> && cd curriculum
npm install
npm run dev        # http://localhost:4321
```

## Scripts

| Command | Description |
| ------- | ----------- |
| `npm run dev` | Dev server com hot reload |
| `npm run build` | Build estatico para producao |
| `npm run preview` | Preview local do build |
| `npm run lint` | ESLint |
| `npm run format` | Prettier |
| `py generate_cvs.py` | Gera 12 CVs markdown (4 roles x 3 langs) |

## Architecture

```text
Browser -> NGINX (SSL + headers) -> dist/ (HTML estatico)
                                      |
Design (Figma) -> Tokens (CSS vars) -> Tailwind -> Astro components
                                      |
Data (cv.json) -> Content Collections -> Pages (/pt/, /en/, /es/)
```

## Documentation

| Doc | Content |
| --- | ------- |
| [AGENTS.md](AGENTS.md) | Agent governance & project rules |
| [docs/adr/](docs/adr/) | 9 Architecture Decision Records |
| [docs/guides/figma-design-system.md](docs/guides/figma-design-system.md) | Figma design system guide |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Dev setup & workflows |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | CI/CD & NGINX config |
| [docs/SECURITY.md](docs/SECURITY.md) | Security practices |

## Principles

- **KISS** — HTML/CSS first, JS only when needed
- **YAGNI** — Don't build it until you need it
- **DRY** — Single source of truth (`cv.json`, `ui.ts`, CSS vars)
- **Clean Code** — Meaningful names, small functions, no dead code

## License

Copyright 2026 Thales Ferreira. All rights reserved.
