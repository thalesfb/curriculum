# ADR-0010: Google Analytics 4 (GA4) para métricas de audiência

## Status

Accepted

## Data

2026-04-17

## Contexto

Precisamos de métricas de audiência do portfolio (páginas visitadas, origem de tráfego, dispositivos, idiomas) para avaliar o alcance profissional e otimizar conteúdo ao longo do tempo. O projeto já tem SEO configurado (Open Graph, hreflang, JSON-LD) mas não tem instrumentação de analytics.

## Decision Drivers

- Custo: zero (conta GA já existe)
- Esforço: mínimo (script oficial do Google)
- Privacidade: respeitar LGPD/GDPR no longo prazo
- Performance: não degradar métricas de PageSpeed
- KISS (ADR-0006): solução mais simples que funciona

## Opções Consideradas

### Opção 1: Google Analytics 4 (gtag.js oficial)

- **Prós**: Zero custo, ecossistema maduro, integra com Search Console, relatórios prontos
- **Contras**: Cookies de terceiros, implicações de privacidade, ~45KB de JS

### Opção 2: Plausible / Umami (analytics privacy-first)

- **Prós**: Sem cookies, leve (<1KB), cumpre LGPD por padrão
- **Contras**: Self-hosted (Umami) aumenta superfície de manutenção, Plausible é pago

### Opção 3: Sem analytics

- **Prós**: Zero impacto em performance e privacidade
- **Contras**: Voar às cegas sobre alcance do portfolio

## Decisão

Adotar **Google Analytics 4** com Measurement ID `G-EF4YKB3P5F`, carregado apenas em produção via `import.meta.env.PROD`.

## Racional

1. **KISS**: snippet oficial do Google, zero dependências npm
2. **Hardcoded**: ID do GA é público (aparece no HTML de qualquer forma), não há ganho em envvar
3. **Apenas produção**: evita poluir métricas com `npm run dev` e previews locais
4. **`is:inline`**: impede que o Astro otimize/bundle o snippet, preservando o comportamento oficial

## Consequências

### Positivas

- Visibilidade sobre alcance geográfico e de dispositivos
- Sem custo financeiro ou de manutenção
- Implementação reversível (deletar 2 blocos de código)

### Negativas

- Adiciona ~45KB de JS em produção (assíncrono, não bloqueia render)
- Requer manutenção futura de conformidade LGPD (banner de consentimento se expandir público para UE)
- CSP precisou ser expandida para permitir `googletagmanager.com` e `google-analytics.com`

### Riscos e mitigações

- **Risco**: bloqueadores de anúncios reduzem precisão → aceitável para portfolio
- **Risco**: regulação LGPD/GDPR futura → mitigar com banner de consentimento se necessário
- **Mitigação**: IP anonymization é default no GA4

## Referências

- [GA4 Setup Guide](https://developers.google.com/analytics/devguides/collection/ga4)
- [Astro `is:inline` directive](https://docs.astro.build/en/reference/directives-reference/#isinline)
- ADR-0006 (KISS)
