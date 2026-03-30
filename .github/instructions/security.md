# Security Instructions

## Never commit

- `.env` files (use `.env.example` with placeholders)
- API keys, tokens, passwords
- SSH keys or certificates
- Database credentials

## Code practices

- Sanitize all user input from contact form (server-side)
- Use `rel="noopener noreferrer"` on external links
- Use `target="_blank"` only when necessary
- No inline `onclick` handlers (use event listeners)
- No `eval()` or `innerHTML` with user data
- Use `set:html` in Astro only with trusted content

## Headers (NGINX)

Required security headers (see docs/SECURITY.md):
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `Content-Security-Policy`
- `Strict-Transport-Security` (HSTS)
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=()`

## Dependencies

- Run `npm audit` before deploying
- No dependencies with known critical vulnerabilities
- Prefer well-maintained packages (last update < 6 months)
