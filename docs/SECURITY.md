# Segurança

## SSL/TLS

- TLS 1.2 e 1.3 apenas (desabilitar TLS 1.0/1.1)
- Certificado via Let's Encrypt com renovação automática (certbot)
- HSTS habilitado com `max-age=31536000; includeSubDomains`

## Security Headers

| Header | Valor | Propósito |
| --- | --- | --- |
| `X-Frame-Options` | `SAMEORIGIN` | Prevenir clickjacking |
| `X-Content-Type-Options` | `nosniff` | Prevenir MIME sniffing |
| `X-XSS-Protection` | `1; mode=block` | Proteção XSS legacy |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controlar referrer |
| `Content-Security-Policy` | Ver NGINX config | Prevenir XSS/injection |
| `Permissions-Policy` | `camera=(), microphone=()` | Restringir APIs |

## Práticas

### Código

- Sem secrets em código (usar GitHub Secrets / .env)
- `.env` no `.gitignore` — sempre
- `.env.example` com placeholders documentados
- Sanitizar inputs do formulário de contato (server-side)
- Dependências auditadas: `npm audit` no CI

### Servidor

- SSH apenas com chave (desabilitar password auth)
- Firewall: apenas portas 80, 443, SSH
- Usuário non-root para NGINX
- Logs de acesso rotacionados

### CI/CD

- Secrets via GitHub Encrypted Secrets
- Permissions mínimas no workflow (`contents: read`)
- Sem `--no-verify` em hooks

## .env.example

```bash
# Formulário de contato
CONTACT_EMAIL=thalesfb15@gmail.com
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_USER=
# SMTP_PASS=

# Analytics (opcional)
# PUBLIC_ANALYTICS_ID=
```

## Checklist de Segurança

- [ ] SSL A+ no [SSL Labs](https://www.ssllabs.com/ssltest/)
- [ ] Headers verificados no [SecurityHeaders.com](https://securityheaders.com/)
- [ ] `npm audit` sem vulnerabilidades críticas
- [ ] Sem secrets no repositório (`git log --all -p | grep -i secret`)
- [ ] `.env` no `.gitignore`
- [ ] CORS configurado se necessário
