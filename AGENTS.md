# AGENTS.md

Governance and instructions for AI agents (Claude Code, GitHub Copilot) working on this repository.

> **CLAUDE.md** is a symlink to this file.

---

## 1. Project Identity

**Project:** Portfolio & CV website for Thales Ferreira
**Domain:** thales.optimizr.site
**Stack:** Astro 5/6 + Tailwind CSS 4 + Vanilla JS
**Owner:** Thales Ferreira (Full Stack Data Engineer | Python & ML | DevOps)
**Language:** Brazilian Portuguese (pt-BR). Respond in Portuguese unless asked otherwise.

---

## 2. Agent Role & Boundaries

### What you ARE

A **technical contributor** that implements, fixes, documents and refactors code following existing ADRs and project conventions. You execute decisions, not make architectural ones.

### What you are NOT

An architect or decision-maker. You do not create new architectural decisions, introduce new dependencies, or change the project's direction without explicit approval.

---

## 3. Risk Classification

Every operation falls into one of three levels:

| Level | Definition | Examples | Approval |
|-------|-----------|----------|----------|
| **SAFE** | Read-only, reversible, local | Read files, search code, run dev server, lint, format, git status | Autonomous |
| **YELLOW** | Writes that follow existing patterns | Edit code per ADRs, create components per design system, update docs, git commit | Autonomous with validation |
| **RED** | Irreversible, architectural, or affects shared state | New dependencies, deploy to production, change DB schema, create new ADRs, git push, force operations | **Requires human approval** |

### RED operations checklist (ask before doing)

- [ ] Adding new npm/pip dependencies
- [ ] Creating or modifying ADRs
- [ ] Pushing to remote / creating PRs
- [ ] Deploying to production (VPS)
- [ ] Changing `data/cv.json` schema (breaking)
- [ ] Modifying Tailwind config architecture
- [ ] Any `--force` or destructive git operations

---

## 4. Allowed Operations

- Implement features per existing ADRs (0001-0009)
- Create/modify Astro components following ADR-0004 (Figma -> CSS -> Tailwind)
- Update Figma design system (variables, components, bindings) via Figma MCP
- Fix CSS using custom properties (never hardcode colors)
- Generate CV variants via `py generate_cvs.py`
- Refactor code for KISS/YAGNI/DRY compliance (ADR-0006, ADR-0009)
- Update documentation (docs/, AGENTS.md)
- Create git commits with conventional commit format
- Run Context7 MCP for up-to-date library documentation

---

## 5. Forbidden Operations

- Create new ADRs without explicit approval
- Add new dependencies without approval (suggest alternatives)
- Change deployment strategy or NGINX config without approval
- Modify core Tailwind architecture (`darkMode`, theme structure)
- Add new color tokens outside ADR-0004 token system
- Deploy to production without explicit request
- Create breaking changes to `data/cv.json` schema
- Skip pre-commit hooks or use `--no-verify`
- Use `git push --force` on main

---

## 6. Repository Structure

```text
curriculum/
├── AGENTS.md / CLAUDE.md        <- Agent governance (this file, symlinked)
├── README.md                    <- Project overview & quick start
├── CHANGELOG.md                 <- Version history (conventional commits)
├── .prettierrc                  <- Code formatting (Tailwind plugin)
├── .github/
│   ├── workflows/deploy.yml     <- CI/CD pipeline
│   └── instructions/            <- AI agent instructions (categorized)
├── data/
│   └── cv.json                  <- Single source of truth (ADR-0005)
├── generate_cvs.py              <- 12 CV variants (4 roles x 3 langs)
├── output/                      <- Generated CV markdowns
├── refs/                        <- Reference PDFs
├── docs/
│   ├── adr/                     <- Architecture Decision Records (9 ADRs)
│   ├── guides/
│   │   └── figma-design-system.md
│   ├── DEVELOPMENT.md
│   ├── DEPLOYMENT.md
│   └── SECURITY.md
└── src/                         <- Astro project (when initialized)
    ├── components/
    ├── content/
    ├── i18n/
    ├── layouts/
    ├── pages/
    └── styles/
```

---

## 7. Tech Stack (ADR-0001)

| Layer | Technology | ADR |
|-------|-----------|-----|
| Framework | Astro 5/6 (zero JS default) | ADR-0001 |
| Styling | Tailwind CSS 4 (`darkMode: "selector"`) | ADR-0001 |
| Interactivity | Vanilla JS (CSS-first) | ADR-0006 |
| i18n | Astro routing `/pt/`, `/en/`, `/es/` | ADR-0003 |
| Data | `data/cv.json` (single source) | ADR-0005 |
| Design | Figma -> CSS Custom Properties -> Tailwind | ADR-0004 |
| Deploy | VPS + NGINX + GitHub Actions | ADR-0002 |
| Environment | Devcontainer + Git Worktrees + MCPs | ADR-0007 |
| Principles | KISS, YAGNI, DRY, Clean Code | ADR-0006, ADR-0009 |

---

## 8. Figma Design System

**File key:** `UXq2erOANKQqaWegZQ9nk1`
**Full guide:** `docs/guides/figma-design-system.md`

### Pages

- **Design** -- Desktop 1440px, Tablet 1024px, Mobile 375px, Menu Overlay
- **Components** -- All master components (Design uses only instances)
- **Style Guide** -- Typography, colors reference

### Variable Collections

| Collection | Type | Modes |
|------------|------|-------|
| Theme | COLOR | Light / Dark (17 vars) |
| i18n | STRING | PT / EN / ES (34 vars) |
| Role | STRING | Data Engineer / Backend / DevOps / Management (4 vars) |

### Key Tokens

| Token | Light | Dark |
|-------|-------|------|
| `bg/page` | `#F8FAFC` | `#0F172A` |
| `bg/card` | `#FFFFFF` | `#1E293B` |
| `text/primary` | `#0F172A` | `#F1F5F9` |
| `text/secondary` | `#64748B` | `#94A3B8` |
| `brand/green` | `#059669` | `#34D399` |
| `border/line` | `#E2E8F0` | `#334155` |

### Components

| Component | Variants |
|-----------|----------|
| Button | Filled / Outline |
| Button Arrow | Active / Inactive |
| Theme Toggle | State=Light / State=Dark |
| WhatsApp Button | State=Default (30% opacity) / State=Hover (100%) |
| Tech Tag, Input Field, Social Icon Button, Section Title, Nav Link, Card Service, Card Project | Single |

### Design Rules

- Logos de marcas (IFC, SENAI, Alura, Red Hat, AWS) manteem cores originais
- Textos em cards: `layoutSizingHorizontal: FILL` (nunca largura fixa)
- Icones vetoriais: fills/strokes bindados a variaveis de cor
- Header fixo via `numberOfFixedChildren` + padding compensatorio no hero
- Carrosseis mobile: swipe only (sem setas). Desktop/Tablet: Button Arrow
- WhatsApp FAB: 56px, fixed acima do footer, link `wa.me/5549998048695`

---

## 9. MCP Servers (ADR-0007)

| MCP | Tools | Use |
|-----|-------|-----|
| **Context7** | `resolve-library-id`, `get-library-docs` | Docs atualizadas de Astro, Tailwind, etc. |
| **Figma** | `get_design_context`, `use_figma`, `get_screenshot` | Design-to-code, tokens, components |

---

## 10. TDD — Test-Driven Development (MANDATORY)

Every feature MUST follow the RED-GREEN-REFACTOR cycle:

1. **RED** — Write a failing test first
2. **GREEN** — Write minimum code to pass
3. **REFACTOR** — Clean up, tests still green

Never write production code without a failing test. Run `npm run test` after every change.

---

## 11. Validation Checklist

Before marking any work as complete, verify:

- [ ] No ADRs were violated
- [ ] Code follows KISS/YAGNI/DRY (ADR-0006, ADR-0009)
- [ ] No hardcoded colors (use CSS custom properties / Tailwind tokens)
- [ ] Dark mode works on all modified components
- [ ] All 3 breakpoints tested (Desktop 1440, Tablet 1024, Mobile 375)
- [ ] i18n strings use variable references (not hardcoded text)
- [ ] Figma components use instances from Components page
- [ ] Conventional commit message format used
- [ ] Documentation updated if behavior changed
- [ ] All tests pass (`npm run test`)
- [ ] Build passes without errors (`npm run build`)

---

## 12. Conventional Commits

```text
:sparkles: feat: new feature
:bug: fix: bug fix
:books: docs: documentation only
:art: style: formatting (no logic change)
:recycle: refactor: code restructuring
:white_check_mark: test: adding tests
:wrench: chore: maintenance (deps, configs)
:zap: perf: performance improvement
:construction_worker: ci: CI/CD changes
```

Format: `:emoji: type(scope): description`
Example: `:sparkles: feat(i18n): add Spanish translations for contact section`

---

## 13. Sources of Truth

| What | Source | Never duplicate in |
|------|--------|--------------------|
| CV content | `data/cv.json` | Components, HTML |
| UI labels | `src/i18n/ui.ts` | Astro templates |
| Color tokens | CSS custom properties | Tailwind classes directly |
| Design specs | Figma file `UXq2erOANKQqaWegZQ9nk1` | Code comments |
| Architecture | `docs/adr/*.md` | AGENTS.md (reference only) |
