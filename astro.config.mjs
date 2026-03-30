// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://thalesfb.curriculum.optimizr.site',
  integrations: [sitemap({
    i18n: {
      defaultLocale: 'pt',
      locales: { pt: 'pt-BR', en: 'en', es: 'es' },
    },
  })],
  i18n: {
    defaultLocale: 'pt',
    locales: ['pt', 'en', 'es'],
    routing: {
      prefixDefaultLocale: true,
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
