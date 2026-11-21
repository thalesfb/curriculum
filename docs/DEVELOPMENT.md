# Guia de Desenvolvimento

## Pré-requisitos

- Node.js 22+
- Python 3.12+ e Typst 0.15.1 (para gerar PDFs)
- Poppler (`pdfinfo`, `pdffonts`, `pdftotext`) para validar PDFs localmente
- Docker (para devcontainer)
- GitHub CLI (`gh`)

## Tipografia e Ativos

- **Tipografia:** Fontes 100% self-hosted em `/fonts/` sob licença SIL OFL (Libertinus Serif e Fira Code). O projeto não utiliza Google Fonts externas nem CDNs para fontes.
- **Imagens:** Foto de perfil em WebP (`/img/profile_hero.webp`, 1024x1024) e Open Graph em JPEG (`/img/profile_hero_og.jpg`, 600x600). Fotos legadas em PNG foram removidas.

## Quick Start

```bash
# Clone
git clone <repo-url> && cd curriculum

# Instalar dependências
npm install

# Dev server
npm run dev
# → http://localhost:4321

# Build estático
npm run build
# → dist/

# Preview do build
npm run preview

# Gerar rascunhos locais de PDF (saída temporária por padrão)
npm run cv:pdf

# Publicar explicitamente PDFs revisados em public/refs
npm run cv:pdf -- --publish-public-refs
```

## Devcontainer

Abra o projeto no VS Code → `Ctrl+Shift+P` → "Reopen in Container".

O devcontainer inclui: Node 22, Python, GitHub CLI, extensões do Astro e Tailwind.

## Git Worktrees

```bash
# Criar worktree para feature
git worktree add ../curriculum-feat-dark-mode feat/dark-mode

# Listar worktrees ativos
git worktree list

# Remover após merge
git worktree remove ../curriculum-feat-dark-mode
```

## MCP Servers

| MCP | Comando |
| --- | --- |
| Context7 | Docs atualizadas: `resolve-library-id` → `get-library-docs` |
| Figma | Design-to-code: `get_design_context`, `use_figma` |

## Scripts

| Script | Descrição |
| --- | --- |
| `npm run dev` | Dev server com hot reload |
| `npm run build` | Build estático para produção |
| `npm run preview` | Preview local do build |
| `npm run lint` | ESLint |
| `npm run format` | Prettier |
| `npm run cv:pdf` | Gera rascunhos PDF em pasta temporária; não substitui `public/refs` |

O gerador usa `data/cv.json` e `cv/cv.typ`; os arquivos DOCX são referências históricas. A saída padrão é temporária e os PDFs públicos não são regenerados no build nem publicados pela CI. Substituir `public/refs` exige revisão visual e a flag `--publish-public-refs`. Veja a [ADR-0011](adr/0011-geracao-pdf-cv-typst.md) e a [proposta do PDF](proposals/0001-cv-pdf.md).

## Conventional Commits

```
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação (sem mudança de lógica)
refactor: refatoração
test: testes
chore: manutenção (deps, configs)
```

Exemplo: `feat(i18n): add Spanish translations`
