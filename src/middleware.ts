import { defineMiddleware } from 'astro:middleware';

export const onRequest = defineMiddleware(async (context, next) => {
  const response = await next();

  // Security Headers — Protection against common web vulnerabilities
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set(
    'Permissions-Policy',
    'geolocation=(), microphone=(), camera=(), payment=()'
  );

  // Additional security headers
  response.headers.set('X-XSS-Protection', '1; mode=block');

  // CORS configuration (if API endpoints exist)
  if (context.url.pathname.startsWith('/api/')) {
    response.headers.set(
      'Access-Control-Allow-Origin',
      'https://thales.optimizr.site'
    );
    response.headers.set(
      'Access-Control-Allow-Methods',
      'GET, POST, OPTIONS'
    );
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type');
  }

  return response;
});
