# ADR-0006: Princípio KISS — HTML/CSS primeiro, JS só quando necessário

## Status

Accepted

## Data

2026-03-28

## Contexto

O portfolio é um site de conteúdo com poucos pontos de interatividade (theme toggle, menu mobile, carrossel, formulário de contato). Precisamos definir quando usar JavaScript e quando resolver com HTML/CSS puro.

## Decision Drivers

* Performance: Menos JS = carregamento mais rápido
* Acessibilidade: HTML semântico funciona sem JS
* Manutenibilidade: CSS é mais previsível que JS para layout
* SEO: Conteúdo em HTML estático é indexado imediatamente

## Decisão

**HTML/CSS puro** para tudo que for possível. **Vanilla JS** apenas quando CSS não resolver. **Nenhum framework reativo** (React, Vue, Svelte).

### Matriz de decisão

| Funcionalidade | Solução | Motivo |
|----------------|---------|--------|
| Menu hamburger mobile | CSS (checkbox hack ou `<details>`) | Animação de abrir/fechar é CSS |
| Dark mode toggle | Vanilla JS (class toggle + localStorage) | Precisa persistir preferência |
| Carrossel de projetos | CSS `scroll-snap` + Vanilla JS para setas | Scroll nativo é performático |
| Formulário de contato | HTML `<form>` + Vanilla JS para envio | Precisa de fetch API |
| Smooth scroll | CSS `scroll-behavior: smooth` | Nativo, sem JS |
| Animações de entrada | CSS `@keyframes` + `IntersectionObserver` | Observer é leve |
| Seletor de idioma | Link `<a href="/en/">` | Navegação simples |
| Barra de pesquisa | CSS + Vanilla JS (filter) | Precisa manipular DOM |

### Regra

> Para cada componente interativo, primeiro avaliar se dá para fazer em CSS puro.
> Só usar Vanilla JS quando CSS não resolver.
> Nunca adicionar uma lib/framework para um único componente.

## Consequências

### Positivas

- Zero JavaScript em 70%+ das interações
- Bundle final mínimo (estimativa < 5KB de JS)
- Funciona com JS desabilitado (graceful degradation)
- Código auditável — sem abstrações de framework

### Negativas

- Menu hamburger CSS é menos flexível que JS (limitações de animação)
- Sem componentes reativos — estado precisa ser gerenciado manualmente
- CSS checkbox hack é menos semântico que `<dialog>` (mitigação: usar `<details>`)

## Referências

- [CSS-only hamburger menu](https://css-tricks.com/three-css-alternatives-to-javascript-navigation/)
- [CSS scroll-snap](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll_snap)
- [Dark mode with CSS + JS](https://hollos.dev/blog/adding-dark-mode-to-your-astro-website-with-tailwind/)
