# Tailwind CSS Styling Instructions

## Dark mode

Use `selector` strategy. Toggle `.dark` class on `<html>`.

```html
<!-- Light: bg white. Dark: bg slate-900 -->
<div class="bg-bg-card text-text-primary">
```

## Custom tokens (from Figma)

All colors map to CSS custom properties:

```css
/* src/styles/global.css */
:root {
  --color-bg-page: #F8FAFC;
  --color-text-primary: #0F172A;
  --color-brand-green: #059669;
}
:root.dark {
  --color-bg-page: #0F172A;
  --color-text-primary: #F1F5F9;
  --color-brand-green: #34D399;
}
```

## Rules

- NEVER hardcode hex colors in classes. Use token-based classes (`bg-bg-page`, `text-text-primary`)
- Use responsive prefixes: `md:` (tablet 1024px), `lg:` (desktop 1440px)
- Use `@apply` sparingly, only for highly reused patterns
- Prettier plugin sorts Tailwind classes automatically
- Mobile-first: base styles for 375px, then `md:` and `lg:` overrides
