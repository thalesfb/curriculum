# Astro Component Instructions

## File naming

- Components: `PascalCase.astro` (e.g. `CardProject.astro`)
- Layouts: `PascalCase.astro` (e.g. `BaseLayout.astro`)
- Pages: `kebab-case.astro` or `index.astro`

## Component structure

```astro
---
// 1. Imports
import TechTag from './TechTag.astro';

// 2. Props interface
interface Props {
  title: string;
  description: string;
}

// 3. Destructure props
const { title, description } = Astro.props;
---

<!-- 4. Template (HTML) -->
<article class="card">
  <h3>{title}</h3>
  <p>{description}</p>
</article>

<!-- 5. Scoped styles (only if needed beyond Tailwind) -->
```

## Rules

- Use Tailwind classes for styling (no scoped CSS unless absolutely needed)
- Use CSS custom properties for design tokens (`var(--color-bg-card)`)
- No `client:load` unless the component MUST be interactive
- Prefer `client:visible` over `client:load` for below-fold components
- Props interface is mandatory for type safety
- Content from cv.json via Content Collections, not hardcoded
- i18n labels from `src/i18n/ui.ts`, not hardcoded strings
