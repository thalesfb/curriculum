# ADR-0002: Deploy em VPS própria

## Status

Accepted

## Data

2026-03-28

## Contexto

O portfolio precisa de hospedagem. O domínio é `thales.optimizr.site`, já configurado. O proprietário possui VPS própria com experiência em DevOps (NGINX, Docker, CI/CD).

## Opções Consideradas

### Opção 1: VPS própria (NGINX + deploy manual/CI)

- **Prós**: Controle total, custo fixo já pago, domínio customizado, experiência DevOps do proprietário, demonstra skills de infraestrutura
- **Contras**: Manutenção de servidor, SSL manual (Let's Encrypt), sem CDN global nativo

### Opção 2: Cloudflare Pages

- **Prós**: CDN global gratuito, deploy automático via git, SSL automático, dona da Astro
- **Contras**: Menos controle, domínio .pages.dev se não configurar custom domain

### Opção 3: Vercel

- **Prós**: DX excelente, preview deploys, analytics, edge functions
- **Contras**: Limites do plano free, vendor lock-in, domínio .vercel.app

## Decisão

Deploy na **VPS própria** com NGINX como servidor web/proxy reverso.

## Racional

1. **Demonstra competência DevOps** — o próprio portfolio é prova de skills de infraestrutura
2. **Custo zero adicional** — VPS já está paga e em uso
3. **Controle total** — headers de segurança, cache, compressão, redirects
4. **Domínio próprio** configurado: thales.optimizr.site

## Consequências

### Positivas

- Portfolio serve como case de DevOps (NGINX config, SSL, deploy)
- Latência baixa para audiência brasileira (VPS no Brasil)
- Sem limites de bandwidth ou builds

### Negativas

- Sem CDN global (mitigação: Cloudflare como proxy/CDN se necessário)
- SSL via Let's Encrypt precisa renovação (automatizável com certbot)
- Sem preview deploys automáticos (mitigação: script de deploy)

## Implementação

- NGINX serve `dist/` gerado pelo `astro build`
- Compressão gzip/brotli habilitada
- SSL via Let's Encrypt + certbot auto-renew
- Deploy via `rsync` ou `git pull` + rebuild no servidor
