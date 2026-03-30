# ADR-0003: Estratégia de i18n com 3 idiomas

## Status

Accepted

## Data

2026-03-28

## Contexto

O portfolio precisa suportar 3 idiomas (PT-BR, EN, ES) para alcançar oportunidades internacionais. Além disso, existem 4 variantes de cargo (Data Engineer, Backend, DevOps, Management), totalizando potencialmente 12 variantes de CV.

O Figma já implementa i18n via Variable Modes na coleção i18n com 34 variáveis STRING.

## Decision Drivers

* SEO: Cada idioma precisa de URL própria com hreflang
* Manutenibilidade: Traduções centralizadas, não espalhadas no código
* Consistência: Figma e código usam a mesma estrutura de dados
* Performance: Sem carregamento de todos os idiomas — apenas o ativo

## Decisão

Usar **Astro i18n routing** com diretórios por idioma (`/pt/`, `/en/`, `/es/`) e arquivo centralizado de traduções TypeScript.

## Estrutura

```
src/
  i18n/
    ui.ts         ← Labels da UI (botões, seções, nav)
    utils.ts      ← Helpers: getLangFromUrl(), useTranslations()
  pages/
    pt/
      index.astro ← Página principal em PT
    en/
      index.astro
    es/
      index.astro
    index.astro   ← Redirect para /pt/ (idioma padrão)
  content/
    cv.json       ← Dados do CV com campos { pt, en, es }
```

### Formato das traduções (ui.ts)

```typescript
export const ui = {
  pt: {
    'nav.home': 'Home',
    'nav.about': 'Sobre',
    'nav.services': 'Serviços',
    'nav.portfolio': 'Portfólio',
    'nav.contact': 'Contato',
    'hero.greeting': '👋 Olá, eu sou Thales Ferreira',
    'cta.hire': 'Contratar',
    'cta.download': 'Baixar CV',
  },
  en: { ... },
  es: { ... },
} as const;
```

### Dados do CV (cv.json)

Campos de texto multilíngue:
```json
{
  "summary": {
    "pt": "Experiência abrangente em...",
    "en": "Comprehensive experience in...",
    "es": "Experiencia integral en..."
  }
}
```

## Consequências

### Positivas

- URLs limpas: `/pt/`, `/en/`, `/es/` — bom para SEO
- hreflang automático via `<link rel="alternate">`
- Tradução carregada apenas para o idioma ativo (zero overhead)
- Dados do cv.json reutilizados para gerar CVs ATS (12 markdowns)

### Negativas

- 3x mais páginas geradas no build (mínimo, site é pequeno)
- Traduções manuais (sem serviço automático)
- Manutenção de 3 versões de textos

## Referências

- [i18n in Astro 5](https://medium.com/@paul.pietzko/internationalization-i18n-in-astro-5-78281827d4b4)
- [Astro i18n Recipes](https://docs.astro.build/en/recipes/i18n/)
