# ADR-0001: Stack do projeto — Astro + Tailwind CSS + Vanilla JS

## Status

Accepted

## Data

2026-03-28

## Contexto

Precisamos escolher a stack de desenvolvimento para o portfolio profissional de Thales Ferreira (thales.optimizr.site). O site é um portfolio/CV com:

- Conteúdo majoritariamente estático (seções: hero, sobre, serviços, projetos, contato)
- Dark mode com toggle
- i18n em 3 idiomas (PT/EN/ES)
- 4 variantes de cargo profissional
- Formulário de contato que envia email
- Design system já definido no Figma com variáveis e tokens
- Deploy em VPS própria

Prioridades: **performance**, **SEO**, **simplicidade**, **manutenibilidade**.

## Decision Drivers

* **Performance**: Portfolio precisa de PageSpeed 95+, carregamento < 1s
* **SEO**: Precisa ranquear bem para "Data Engineer", "DevOps", etc.
* **Simplicidade (KISS)**: Mínimo de JavaScript, mínimo de dependências
* **Design fidelity**: Tokens do Figma devem mapear diretamente para código
* **i18n**: Suporte nativo a rotas por idioma com hreflang
* **Manutenção**: Fácil de atualizar conteúdo sem rebuild complexo

## Opções Consideradas

### Opção 1: Astro 5/6 + Tailwind CSS 4 + Vanilla JS

- **Prós**: Zero JS por padrão (ships HTML), Content Collections para JSON, i18n routing nativo, Tailwind mapeia 1:1 com tokens Figma, islands architecture para interatividade seletiva, Cloudflare adquiriu Astro em jan/2026
- **Contras**: Menos familiar que Next.js para quem vem de React

### Opção 2: Next.js 15 + Tailwind CSS

- **Prós**: Ecossistema React, SSG/SSR flexível, App Router maduro
- **Contras**: Envia React runtime (~80KB+) desnecessário para site estático, overhead de complexidade, i18n requer config adicional

### Opção 3: HTML/CSS puro + Vanilla JS

- **Prós**: Máxima simplicidade, zero dependências, controle total
- **Contras**: Sem routing i18n, sem templating para 12 variantes de CV, duplicação de HTML, sem Content Collections

### Opção 4: SvelteKit + Tailwind CSS

- **Prós**: Bundles menores que React, boa DX, SSG suportado
- **Contras**: Menos ecosistema que Astro para conteúdo estático, curva de aprendizado de Svelte

## Decisão

Adotar **Astro 5/6** como framework, **Tailwind CSS 4** para estilização, e **Vanilla JS** (sem framework reativo) para interatividade mínima.

## Racional

1. **Astro ships zero JS por padrão** — perfeito para portfolio estático com SEO máximo
2. **Content Collections com file() loader** lê diretamente o `cv.json` existente com validação Zod
3. **Tailwind CSS 4 `darkMode: "selector"`** mapeia direto das variáveis Figma para CSS custom properties
4. **Vanilla JS** para os poucos componentes interativos (theme toggle com localStorage, menu mobile com CSS checkbox hack, carrossel)
5. **Astro i18n routing** gera `/pt/`, `/en/`, `/es/` com hreflang automático
6. **Islands architecture** (`client:load`, `client:visible`) hidrata apenas o necessário

O overhead de Next.js não se justifica para um site sem estado de aplicação. HTML/CSS puro não escala para 12 variantes (4 cargos × 3 idiomas).

## Consequências

### Positivas

- PageSpeed 98-100 esperado (HTML estático com zero JS por padrão)
- Tokens Figma → Tailwind config → classes utilitárias (pipeline direto)
- Content Collections tipam o cv.json em build time
- Deploy simples: `astro build` gera pasta `dist/` com HTML estático

### Negativas

- Time precisa aprender Astro syntax (`.astro` files, frontmatter)
- Ecossistema menor que Next.js para plugins
- Sem React = componentes interativos em Vanilla JS

### Riscos

- Se o site evoluir para webapp (dashboard, CMS), Astro pode ser limitante
- Mitigação: Astro suporta SSR com adapters, pode adicionar React islands

## Referências

- [Astro 5 vs Next.js 15 Comparison 2026](https://wppoland.com/en/astro-5-vs-nextjs-15-comparison-2026/)
- [Astro Content Collections Guide](https://inhaq.com/blog/getting-started-with-astro-content-collections.html)
- [Cloudflare adquiriu Astro (jan/2026)](https://dev.to/polliog/astro-in-2026)
