# ADR-0007: Ambiente de Desenvolvimento — Devcontainer, Worktrees e MCPs

## Status

Accepted

## Data

2026-03-28

## Contexto

Precisamos definir o ambiente de desenvolvimento padronizado para garantir reprodutibilidade, produtividade e integração com ferramentas de IA. O projeto usa Astro + Tailwind e será desenvolvido com assistência de Claude Code.

## Decisão

### 1. Devcontainer

Usar **Dev Containers** (VS Code) para padronizar o ambiente de desenvolvimento.

```json
{
  "name": "portfolio-thales",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:22",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "forwardPorts": [4321],
  "postCreateCommand": "npm install",
  "customizations": {
    "vscode": {
      "extensions": [
        "astro-build.astro-vscode",
        "bradlc.vscode-tailwindcss",
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode"
      ]
    }
  }
}
```

**Racional:** Qualquer pessoa (ou CI) clona o repo e tem o mesmo ambiente. Node 22, Python (para `generate_cvs.py`), GitHub CLI, extensões do Astro e Tailwind.

### 2. Git Worktrees

Usar **git worktrees** para trabalhar em múltiplas branches simultaneamente sem stash/switch.

```bash
# Criar worktree para feature
git worktree add ../curriculum-feat-i18n feat/i18n

# Criar worktree para hotfix
git worktree add ../curriculum-hotfix hotfix/typo

# Listar worktrees
git worktree list

# Remover após merge
git worktree remove ../curriculum-feat-i18n
```

**Racional:** Permite desenvolver features em paralelo sem conflitos de estado. Agentes Claude Code podem trabalhar em worktrees isolados via `isolation: "worktree"`.

### 3. MCP Servers

Servidores MCP (Model Context Protocol) integrados ao Claude Code:

| MCP Server | Propósito | Uso no projeto |
|------------|-----------|---------------|
| **Context7** | Documentação atualizada de libs em tempo real | Consultar docs do Astro 5/6, Tailwind CSS 4, APIs |
| **Figma** | Leitura/escrita no Figma via Plugin API | Extrair tokens, criar componentes, auditar design |

#### Context7 MCP

```
Tools: resolve-library-id, get-library-docs
Uso: Antes de implementar qualquer feature, consultar docs atualizadas
Exemplo: "astro i18n routing" → retorna docs mais recentes do Astro 5/6
```

#### Figma MCP

```
Tools: get_design_context, get_screenshot, use_figma, get_metadata
Uso: Extrair tokens de design, verificar componentes, criar elementos
Exemplo: get_design_context(nodeId) → retorna código + screenshot do componente
```

## Consequências

### Positivas

- Ambiente 100% reprodutível via devcontainer
- Worktrees permitem desenvolvimento paralelo sem conflitos
- MCPs fornecem documentação atualizada e acesso direto ao Figma
- Claude Code pode trabalhar em branches isolados

### Negativas

- Devcontainer requer Docker instalado
- MCPs precisam de autenticação configurada

## Referências

- [Dev Containers Specification](https://containers.dev/)
- [Git Worktrees](https://git-scm.com/docs/git-worktree)
- [Context7 MCP](https://github.com/upstash/context7)
- [Figma MCP](https://github.com/anthropics/claude-figma-mcp)
