# Guia de Desenvolvimento

## Pré-requisitos

- Node.js 22+
- Python 3.12+ (para gerar rascunhos locais de PDF)
- Docker (para devcontainer)
- GitHub CLI (`gh`)

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

# Gerar rascunhos locais de PDF (Word no Windows)
npm run generate:pdfs

# Publicar explicitamente PDFs revisados em public/refs
npm run generate:pdfs -- --output-dir public/refs --publish-public-refs
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
| `npm run generate:pdfs` | Gera rascunhos PDF em pasta temporária; não substitui `public/refs` |

O gerador usa `data/cv.json` e o DOCX como entradas de rascunho. Os PDFs publicados são artefatos aprovados e seu conteúdo não é regenerado no build nem na CI. Substituir `public/refs` exige revisão do conteúdo e as flags `--output-dir public/refs --publish-public-refs`. Não há gerador de CV Markdown neste repositório.

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
