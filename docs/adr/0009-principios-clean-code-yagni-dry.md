# ADR-0009: Princípios de Código — Clean Code, YAGNI, DRY

## Status

Accepted

## Data

2026-03-28

## Contexto

Precisamos definir os princípios e padrões de qualidade de código que guiarão o desenvolvimento do portfolio. O projeto é pequeno mas deve servir como vitrine profissional — o código-fonte é parte do portfólio.

## Decisão

Adotar os seguintes princípios como guia de desenvolvimento:

### 1. KISS — Keep It Simple, Stupid (ADR-0006)

> A solução mais simples que funciona é a melhor.

- HTML/CSS puro antes de JS
- Sem abstrações prematuras
- Sem libs para resolver o que 10 linhas de código resolvem

### 2. YAGNI — You Aren't Gonna Need It

> Não implemente algo até que seja realmente necessário.

| Não fazer | Fazer |
|-----------|-------|
| Sistema de CMS para editar conteúdo | Editar `cv.json` direto |
| Cache layer com Redis | HTML estático (já é cache) |
| Framework de testes E2E | Testes manuais + Lighthouse |
| Sistema de autenticação | Links públicos |
| API REST para dados | Content Collections do Astro |
| Micro-frontends | Componentes `.astro` simples |

### 3. DRY — Don't Repeat Yourself

> Cada pedaço de conhecimento deve ter uma representação única e autoritativa.

Aplicação no projeto:

| Dado | Source of Truth | Consumidores |
|------|----------------|--------------|
| Conteúdo profissional | `data/cv.json` | Astro, `generate_cvs.py`, Figma |
| Labels da UI | `src/i18n/ui.ts` | Todos os componentes Astro |
| Tokens de cor | CSS Custom Properties | Tailwind config, componentes |
| Layout de seção | Componente `Section.astro` | Todas as seções da página |
| Card de projeto | Componente `CardProject.astro` | Seção de projetos (loop) |

### 4. Clean Code

Regras aplicáveis ao projeto:

- **Nomes significativos**: `CardProject.astro` não `CP.astro`
- **Funções pequenas**: Uma função faz uma coisa
- **Sem comentários óbvios**: O código deve ser autoexplicativo
- **Sem código morto**: Nada comentado "para depois"
- **Formatação consistente**: Prettier com config padrão
- **Sem magic numbers**: Usar tokens/variáveis CSS

### 5. Convenções de código

```
Componentes Astro:  PascalCase      → CardProject.astro
Layouts:            PascalCase      → BaseLayout.astro
Utilitários:        camelCase       → useTranslations.ts
CSS classes:        kebab-case      → .whatsapp-fab
Variáveis CSS:      --prefix-name   → --color-bg-page
Arquivos JSON:      kebab-case      → cv.json
Diretórios:         kebab-case      → docs/adr/
```

## Consequências

### Positivas

- Código limpo é parte do portfólio — demonstra profissionalismo
- Menos código = menos bugs = mais fácil de manter
- Princípios são familiar para qualquer dev que revisar
- YAGNI evita scope creep

### Negativas

- DRY excessivo pode levar a abstrações prematuras (balancear com KISS)
- Clean Code é subjetivo em edge cases

### Regra de desempate

> Quando KISS e DRY conflitarem, KISS vence.
> 3 linhas repetidas são melhores que uma abstração prematura.

## Referências

- Clean Code — Robert C. Martin
- The Pragmatic Programmer — David Thomas, Andrew Hunt
- YAGNI — Martin Fowler (martinfowler.com/bliki/Yagni.html)
