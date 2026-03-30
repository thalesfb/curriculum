# ADR-0004: Design System — Pipeline Figma → Código

## Status

Accepted

## Data

2026-03-28

## Contexto

O design system do portfolio está definido no Figma com 3 coleções de variáveis (Theme, i18n, Role), 10+ componentes, e layouts para 3 breakpoints. Precisamos definir como esses tokens e componentes serão consumidos no código.

## Decisão

Mapear variáveis Figma → CSS Custom Properties → Tailwind CSS config.

### Pipeline

```
Figma Variables          →  CSS Custom Properties     →  Tailwind Config
─────────────────────────────────────────────────────────────────────────
bg/page: #F8FAFC         →  --color-bg-page: #F8FAFC  →  bg-page
bg/card: #FFFFFF          →  --color-bg-card: #FFFFFF   →  bg-card
text/primary: #0F172A     →  --color-text-primary       →  text-primary
brand/green: #059669      →  --color-brand-green         →  text-brand
```

### Dark mode

```css
/* global.css */
:root {
  --color-bg-page: #F8FAFC;
  --color-text-primary: #0F172A;
}

:root.dark {
  --color-bg-page: #0F172A;
  --color-text-primary: #F1F5F9;
}
```

```javascript
// tailwind.config.mjs
export default {
  darkMode: 'selector', // class .dark no <html>
  theme: {
    extend: {
      colors: {
        'bg-page': 'var(--color-bg-page)',
        'bg-card': 'var(--color-bg-card)',
        'text-primary': 'var(--color-text-primary)',
        'brand-green': 'var(--color-brand-green)',
      }
    }
  }
}
```

### Componentes Figma → Astro

| Figma Component | Astro Component | Interatividade |
|-----------------|-----------------|----------------|
| Button (Filled/Outline) | `Button.astro` | Nenhuma (HTML/CSS) |
| Button Arrow (Active/Inactive) | `CarouselNav.astro` | Vanilla JS |
| Theme Toggle | `ThemeToggle.astro` | Vanilla JS + localStorage |
| Tech Tag | `TechTag.astro` | Nenhuma |
| Card Service | `CardService.astro` | Nenhuma |
| Card Project | `CardProject.astro` | Nenhuma |
| Input Field | `InputField.astro` | Nenhuma |
| Lang Selector | `LangSelector.astro` | Nenhuma (link) |

## Consequências

### Positivas

- 1:1 entre Figma e código — designer e dev falam a mesma linguagem
- Dark mode via CSS variables — sem JavaScript para trocar cores
- Tailwind gera apenas as classes usadas (tree-shaking)

### Negativas

- Manutenção manual do mapeamento Figma → CSS (sem sync automático)
- Mudanças no Figma precisam ser refletidas manualmente no código

### Mitigação

- Documentar o mapeamento no guia Figma (`docs/guides/figma-design-system.md`)
- Usar `get_design_context` do Figma MCP para extrair tokens atualizados
