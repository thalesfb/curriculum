# 🎯 Curriculum — Professional Portfolio

**Multilingual portfolio and CV for Thales Ferreira** — Full Stack Data Engineer | Python & ML | DevOps Specialist. High-performance static site with Figma-integrated design system.

[![CI/CD](https://img.shields.io/github/actions/workflow/status/thalesfb/curriculum/ci.yml?branch=main&label=CI%2FCD&style=flat-square)](https://github.com/thalesfb/curriculum/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/actions/workflow/status/thalesfb/curriculum/release.yml?branch=main&label=Release&style=flat-square)](https://github.com/thalesfb/curriculum/actions/workflows/release.yml)
[![Astro](https://img.shields.io/badge/Astro-7.4.13-ff5d01?style=flat-square&logo=astro)](https://astro.build)
[![Tailwind](https://img.shields.io/badge/Tailwind_CSS-4.2-38bdf8?style=flat-square&logo=tailwindcss)](https://tailwindcss.com)

> 🔗 **Quick Navigation**: [Live](#-links) • [Quick Start](#-quick-start) • [Architecture](#️-architecture) • [Documentation](#-documentation)

---

## 🔗 Links

| Resource | URL |
| -------- | --- |
| **Live** | [thalesfb.curriculum.optimizr.site](https://thalesfb.curriculum.optimizr.site) |
| **Design** | [Figma](https://www.figma.com/design/UXq2erOANKQqaWegZQ9nk1/CV?node-id=0-1&m=dev) |
| **Design Guide** | [Figma Design System](docs/guides/figma-design-system.md) |
| **Repository** | [github.com/thalesfb/curriculum](https://github.com/thalesfb/curriculum) |

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
| ----- | ---------- | ------- |
| Framework | **Astro 7.4** | Zero JS default, static output |
| Styling | **Tailwind CSS 4** | CSS custom properties, class-based dark mode |
| Interactivity | **Vanilla JS** | CSS-first, JS only when needed |
| i18n | **Astro Routing** | PT / EN / ES with prefix routing |
| Data | **cv.json** | Single source of truth for all CV content |
| Testing | **Vitest** | 37 unit tests (i18n, data, build) |
| Design | **Figma** | Variables, components, light/dark themes |
| Deploy | **GitHub Actions** | Build → SCP to VPS → NGINX |
| Infrastructure | **VPS + NGINX** | HTTPS, HSTS, CSP headers |

---

## ✨ Features

- 🌍 **Multilingual** — PT, EN, ES with automatic routing and full i18n
- 🎨 **Design System** — Figma → CSS Custom Properties → Tailwind (never hardcoded)
- 🌙 **Dark Mode** — Manual toggle, class-based (Tailwind CSS 4)
- 🔍 **Search** — Real-time filtering of projects and services
- 👔 **5 Roles** — Data Engineer, Backend, DevOps, Management, Frontend (auto-rotation)
- 📱 **Responsive** — Desktop (1440px), Tablet (1024px), Mobile (375px)
- ♿ **Accessible** — ARIA labels, skip-to-content, focus-visible, prefers-reduced-motion
- 🔒 **Secure** — CSP, HSTS, X-Content-Type-Options, Referrer-Policy
- 📊 **SEO** — Open Graph, hreflang, JSON-LD, sitemap, canonical URLs
- 📈 **Analytics** — Google Analytics 4 (production only, CSP-protected)
- ⚡ **Performance** — Zero JS default, optimized WebP/JPEG images, self-hosted fonts (no Google Fonts)

---

## 🚀 Quick Start

### Prerequisites

- Node.js `^22.23.4 || >=24.10.0`
- npm
- Python 3.12+ and Typst 0.15.1 (only when regenerating the downloadable PDFs)
- Poppler tools (`pdfinfo`, `pdffonts`, `pdftotext`) for local PDF validation

### Development

```bash
git clone https://github.com/thalesfb/curriculum.git
cd curriculum
npm install
npm run dev        # http://localhost:4321
```

### Scripts

| Command | Description |
| ------- | ----------- |
| `npm run dev` | Dev server with hot reload |
| `npm run build` | Static build → `dist/` |
| `npm run preview` | Preview production build |
| `npm test` | Run Vitest tests |
| `npm run test:watch` | Tests in watch mode |
| `npm run cv:pdf` | Generate three local PDF drafts from `data/cv.json` |

The Typst generator writes to a temporary folder by default. After reviewing all three PDFs (two pages each in the current release), replace `public/refs` only with `npm run cv:pdf -- --publish-public-refs`. The site build and CI never publish or commit generated PDFs. See [ADR-0011](docs/adr/0011-geracao-pdf-cv-typst.md) for fidelity criteria and the [PDF proposal](docs/proposals/0001-cv-pdf.md) for the decision rationale. Historical DOCX templates remain in `refs/template/` but are not used by the generator.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    FIGMA[Figma Design System]
    CV[cv.json]
    UI[ui.ts i18n]
    ASTRO[Astro Components]
    TW[Tailwind CSS 4]
    DIST[dist/ static]
    GHA[GitHub Actions]
    VPS[VPS + NGINX]

    FIGMA -->|tokens| TW
    CV -->|content| ASTRO
    UI -->|translations| ASTRO
    TW -->|classes| ASTRO
    ASTRO -->|build| DIST
    DIST -->|CI/CD| GHA
    GHA -->|SCP| VPS

    style FIGMA fill:#f3e5f5
    style CV fill:#e8f5e9
    style ASTRO fill:#e1f5ff
    style VPS fill:#fff4e1
```

### Data Flow

```text
Figma (design) → CSS Custom Properties → Tailwind classes → Astro components
cv.json (data)  → Hero, About, Services, Projects → Pages (/pt/, /en/, /es/)
ui.ts (labels)  → All UI text → Translated per language
```

### Deploy Pipeline

```text
Push to main → GitHub Actions (npm test + npm build) → SCP dist/ → VPS → NGINX (HTTPS)
```

---

## 📁 Project Structure

```text
curriculum/
├── .github/workflows/     CI/CD pipelines (ci, build, release)
├── data/cv.json           Single source of truth for CV content
├── docs/
│   ├── adr/               11 Architecture Decision Records
│   ├── guides/            Figma design system guide
│   ├── DEPLOYMENT.md      Deploy & NGINX docs
│   ├── DEVELOPMENT.md     Dev setup & workflows
│   └── SECURITY.md        Security practices
├── cv/                    Typst CV template, vendored imprecv, and Libertinus Serif fonts
├── public/
│   ├── icons/             Tech skill icons (SVG)
│   ├── img/               UI icons + profile photo (WebP/JPEG)
│   ├── logos/             Brand logos (IFC, SENAI, Alura, Red Hat, AWS, Cisco)
│   └── refs/              CV PDFs (PT, EN, ES)
├── src/
│   ├── __tests__/         Build + CV data tests
│   ├── components/        7 Astro components
│   ├── i18n/              ui.ts + utils.ts + tests
│   ├── layouts/           BaseLayout (SEO, OG, JSON-LD)
│   ├── middleware.ts      Security headers
│   ├── pages/             index + /pt/ /en/ /es/
│   └── styles/            Design tokens + global CSS
├── scripts/build_cv_pdf.py Explicit local PDF generation and validation
├── AGENTS.md              AI agent governance
├── astro.config.mjs       Astro + sitemap config
└── package.json           Scripts + dependencies
```

---

## 📚 Documentation

| Doc | Content |
| --- | ------- |
| [AGENTS.md](AGENTS.md) | AI agent governance & project rules |
| [docs/adr/](docs/adr/) | 11 Architecture Decision Records |
| [docs/guides/figma-design-system.md](docs/guides/figma-design-system.md) | Figma design system guide |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Dev setup & workflows |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | CI/CD & NGINX config |
| [docs/SECURITY.md](docs/SECURITY.md) | Security practices |

---

## 🧪 Testing

```bash
npm test
npm run test:watch   # Watch mode
python -m unittest discover -s scripts/tests -v
```

The Python PDF tests validate two-page output, embedded Libertinus Serif fonts, extracted content, accents, and active links in all three languages. Install Typst 0.15.1 and Poppler locally to run the PDF checks; CI installs both automatically. Without those tools, only the integration tests skip with an explicit reason.

---

## 🎨 Design Principles

- **KISS** — HTML/CSS first, JS only when needed
- **YAGNI** — Don't build it until you need it
- **DRY** — Single source of truth (`cv.json`, `ui.ts`, CSS custom properties)
- **Clean Code** — Meaningful names, small functions, no dead code
- **Design-First** — Figma → CSS tokens → Tailwind → Code (never hardcoded colors)

---

## 📄 License

Copyright 2026 Thales Ferreira. All rights reserved.

The vendored CV template is licensed under Apache-2.0 (see `cv/vendor/imprecv/LICENSE` and `NOTICE`). Libertinus Serif is licensed under SIL OFL 1.1 (see `cv/fonts/OFL.txt`).
