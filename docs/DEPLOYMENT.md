# Guia de Deploy

## Infraestrutura

- **Servidor:** VPS própria
- **Web server:** NGINX
- **SSL:** Let's Encrypt + certbot auto-renew
- **Domínio:** thales.optimizr.site
- **CI/CD:** GitHub Actions

## Deploy Manual

```bash
# Build local
npm run build

# Sync para VPS
rsync -avz --delete dist/ user@vps:/var/www/thales.optimizr.site/

# Ou via SSH
ssh user@vps "cd /var/www/thales.optimizr.site && git pull && npm run build"
```

## GitHub Actions (CI/CD)

```yaml
name: Deploy Portfolio
on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - run: npm ci
      - run: npm run build

      - name: Deploy to VPS
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_KEY }}
          port: ${{ secrets.VPS_PORT }}
          source: "dist/*"
          target: "/var/www/thales.optimizr.site"
          strip_components: 1

      - name: Health Check
        run: curl -f https://thales.optimizr.site || exit 1
```

### Secrets necessários

| Secret | Descrição |
| --- | --- |
| `VPS_HOST` | IP ou hostname do servidor |
| `VPS_USER` | Usuário SSH |
| `VPS_KEY` | Chave SSH privada |
| `VPS_PORT` | Porta SSH (default: 22) |

## NGINX Config

```nginx
server {
    listen 443 ssl http2;
    server_name thales.optimizr.site;

    root /var/www/thales.optimizr.site;
    index index.html;

    # SSL
    ssl_certificate /etc/letsencrypt/live/thales.optimizr.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/thales.optimizr.site/privkey.pem;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:;" always;

    # Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback por idioma
    location / {
        try_files $uri $uri/ /pt/index.html;
    }

    # Redirect / to /pt/
    location = / {
        return 302 /pt/;
    }
}

# HTTP → HTTPS redirect
server {
    listen 80;
    server_name thales.optimizr.site;
    return 301 https://$host$request_uri;
}
```

## Checklist de Deploy

- [ ] `npm run build` sem erros
- [ ] Lighthouse score > 95 em todas as métricas
- [ ] Dark mode funcional
- [ ] i18n (PT/EN/ES) todas as rotas funcionam
- [ ] WhatsApp button redireciona corretamente
- [ ] Formulário de contato envia email
- [ ] SSL válido (A+ no SSL Labs)
- [ ] Security headers presentes

## Releases

### Release recovery

The `Release` workflow runs on pushes to `main` and can also be started with `workflow_dispatch`. Runs share a repository-scoped concurrency group and do not cancel an in-progress run. Checkout fetches the full history, tags, and semantic-release Git notes.

On every run, after semantic-release, the workflow compares version tags (`vX.Y.Z`) with GitHub Releases. For a tag without a Release, it creates one with `gh release create --generate-notes`. This reconciliation runs even if semantic-release fails after pushing a tag. A failed semantic-release step only counts as recovered when the workflow publishes a missing Release for a new tag pointing at the current commit; other failures still fail the job.

During backfill, the workflow finds the highest strict semantic-version tag with `sort -V`. Releases for lower tags are created with `--latest=false`, so restoring an older release such as `v1.5.0` cannot replace a newer `v1.6.1` as GitHub's Latest release. The highest tag keeps GitHub CLI's default latest behavior.

The 2026-11-20 failure was run `44658786300` for `v1.5.0`. Its log shows semantic-release passed its Git push authorization check and then GitHub rejected `refs/notes/semantic-release-v1.5.0` with `missing necessary objects`. The `v1.5.0` tag exists but has no GitHub Release. The previous successful run `44657761269` completed at 02:01:35Z; the failing run started at 02:09:41Z, so these runs did not overlap. The repository history had been rewritten on 2026-11-19. Together with the rejected notes ref, this points to stale or unavailable semantic-release note objects after the rewrite rather than a permissions failure or a race. The [semantic-release troubleshooting guide](https://semantic-release.org/support/troubleshooting/) notes that history rewrites can lose release-tracking Git notes. The release workflow now fetches notes explicitly and repairs any tag without its GitHub Release on a later run.
