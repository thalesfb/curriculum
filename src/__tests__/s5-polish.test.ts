import { describe, it, expect } from 'vitest';
import { existsSync, readFileSync } from 'fs';
import { resolve } from 'path';
import cvData from '../../data/cv.json';
import { ui } from '../i18n/ui';

const distDir = resolve(__dirname, '../../dist');
const hasBuild = existsSync(resolve(distDir, 'index.html'));
const decodeHtml = (html: string) => html
  .replace(/&amp;/g, '&')
  .replace(/&#39;|&#x27;/g, "'")
  .replace(/&quot;/g, '"');

describe('PR 3: Brand Logos and Theme Token --color-bg-logo', () => {
  it('defines --color-bg-logo: #FFFFFF in global.css in both @theme and .dark', () => {
    const css = readFileSync(resolve(__dirname, '../styles/global.css'), 'utf-8');
    const themeBlock = css.slice(css.indexOf('@theme'), css.indexOf('}', css.indexOf('@theme')));
    const darkBlock = css.slice(css.indexOf('.dark {'), css.indexOf('}', css.indexOf('.dark {')));
    expect(themeBlock).toMatch(/--color-bg-logo:\s*#FFFFFF/i);
    expect(darkBlock).toMatch(/--color-bg-logo:\s*#FFFFFF/i);
  });

  it('uses bg-bg-logo on logo and neutral icon wrappers in About.astro', () => {
    const astro = readFileSync(resolve(__dirname, '../components/About.astro'), 'utf-8');
    expect(astro).toContain('bg-bg-logo');
    expect(astro).toContain('border-border-line');
    expect(astro).toContain('max-w-[34px]');
  });

  it.skipIf(!hasBuild)('wraps every /logos/ brand image outside the header in an immediate bg-bg-logo parent in built HTML', () => {
    for (const lang of ['pt', 'en', 'es']) {
      const html = readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8');
      const headerEnd = html.indexOf('</header>');
      const bodyHtml = html.slice(headerEnd);

      // Find all img elements using /logos/
      const imgRegex = /<img[^>]+src=["'](\/logos\/[^"']+)["'][^>]*>/g;
      let match: RegExpExecArray | null;
      let logoCount = 0;

      while ((match = imgRegex.exec(bodyHtml)) !== null) {
        // The site's own mark (mobile menu) is not a brand logo.
        if (match[1] === '/logos/logo.svg') continue;
        logoCount++;
        const imgTag = match[0];
        const imgIndex = match.index;
        // Check immediate ancestor by slicing backwards to the previous opening tag
        const preceding = bodyHtml.slice(Math.max(0, imgIndex - 300), imgIndex);
        const lastOpenTag = preceding.slice(preceding.lastIndexOf('<'));
        expect(lastOpenTag).toContain('bg-bg-logo');
      }
      expect(logoCount).toBeGreaterThan(0);
    }
  });
});

describe('PR 3: Hero Profile Photo & Social Meta Images', () => {
  it('has no references to profile_hero.png across the source codebase', () => {
    const baseLayout = readFileSync(resolve(__dirname, '../layouts/BaseLayout.astro'), 'utf-8');
    const hero = readFileSync(resolve(__dirname, '../components/Hero.astro'), 'utf-8');
    expect(baseLayout).not.toContain('profile_hero.png');
    expect(hero).not.toContain('profile_hero.png');
  });

  it('uses /img/profile_hero.webp with 1024x1024 and fetchpriority="high" in Hero.astro', () => {
    const hero = readFileSync(resolve(__dirname, '../components/Hero.astro'), 'utf-8');
    expect(hero).toContain('/img/profile_hero.webp');
    expect(hero).toContain('width="1024"');
    expect(hero).toContain('height="1024"');
    expect(hero).toContain('fetchpriority="high"');
    expect(hero).toContain('decoding="async"');
    expect(hero).not.toContain('loading="lazy"');
  });

  it.skipIf(!hasBuild)('renders /img/profile_hero.webp in Hero and /img/profile_hero_og.jpg in meta tags across all locales', () => {
    for (const lang of ['pt', 'en', 'es']) {
      const html = readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8');
      expect(html).not.toContain('profile_hero.png');
      expect(html).toContain('/img/profile_hero.webp');
      expect(html).toContain('fetchpriority="high"');
      expect(html).toContain('decoding="async"');

      // OG and Twitter images
      expect(html).toContain('property="og:image" content="https://thalesfb.curriculum.optimizr.site/img/profile_hero_og.jpg"');
      expect(html).toContain('name="twitter:image" content="https://thalesfb.curriculum.optimizr.site/img/profile_hero_og.jpg"');
      expect(html).toContain('property="og:image:width" content="600"');
      expect(html).toContain('property="og:image:height" content="600"');
      expect(html).toContain('property="og:image:alt"');
      expect(html).toContain(ui[lang as 'pt' | 'en' | 'es']['og.imageAlt']);
    }
  });
});

describe('PR 3: SEO & JSON-LD Person Schema', () => {
  it.skipIf(!hasBuild)('renders valid JSON-LD Person with CV data, canonical URL, and https sameAs across all routes', () => {
    for (const lang of ['pt', 'en', 'es'] as const) {
      const html = readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8');
      const jsonLdMatch = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
      expect(jsonLdMatch).toBeTruthy();

      const schema = JSON.parse(jsonLdMatch![1]);
      expect(schema['@context']).toBe('https://schema.org');
      expect(schema['@type']).toBe('Person');
      expect(schema.name).toBe(cvData.personal.name);
      expect(schema.email).toBe(cvData.personal.email);
      expect(schema.jobTitle).toBe(cvData.personal.titles['data-engineer'][lang]);
      expect(schema.url).toBe(`https://thalesfb.curriculum.optimizr.site/${lang}/`);
      expect(schema.image).toBe('https://thalesfb.curriculum.optimizr.site/img/profile_hero_og.jpg');

      expect(Array.isArray(schema.sameAs)).toBe(true);
      expect(schema.sameAs).toContain('https://github.com/thalesfb');
      expect(schema.sameAs).toContain('https://linkedin.com/in/thalesfb');
      expect(schema.sameAs).toContain('https://lattes.cnpq.br/9042504768658064');

      for (const url of schema.sameAs) {
        expect(url.startsWith('https://')).toBe(true);
      }
    }
  });
});

describe('PR 3: Accessibility Improvements', () => {
  it.skipIf(!hasBuild)('associates contact form inputs with <label> elements across all routes', () => {
    for (const lang of ['pt', 'en', 'es'] as const) {
      const html = decodeHtml(readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8'));
      const contactSection = html.slice(html.indexOf('id="contact"'));

      expect(contactSection).toMatch(/<label[^>]+for="cf-name"[^>]*>[\s\S]*?<\/label>/);
      expect(contactSection).toMatch(/<input[^>]+id="cf-name"/);
      expect(contactSection).toMatch(/<label[^>]+for="cf-message"[^>]*>[\s\S]*?<\/label>/);
      expect(contactSection).toMatch(/<textarea[^>]+id="cf-message"/);

      expect(contactSection).toContain(ui[lang]['contact.name']);
      expect(contactSection).toContain(ui[lang]['contact.message']);
    }
  });

  it.skipIf(!hasBuild)('configures role="status" and aria-live on the form feedback element', () => {
    for (const lang of ['pt', 'en', 'es'] as const) {
      const html = decodeHtml(readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8'));
      expect(html).toMatch(/<p[^>]+id="cf-status"[^>]+role="status"[^>]+aria-live="polite"/);
      expect(html).toContain(`data-success="${ui[lang]['contact.success']}"`);
    }
  });

  it.skipIf(!hasBuild)('provides meaningful alt text for the site logo in Header and mobile menu', () => {
    for (const lang of ['pt', 'en', 'es'] as const) {
      const html = decodeHtml(readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8'));
      const expectedAlt = ui[lang]['site.logoAlt'];

      // Header logo
      expect(html).not.toMatch(/<img[^>]+src="\/logos\/logo\.svg"[^>]+alt=">_"/);
      expect(html).toContain(`alt="${expectedAlt}"`);
    }
  });

  it.skipIf(!hasBuild)('provides distinct, localized aria-labels for main, mobile, and footer navigation', () => {
    for (const lang of ['pt', 'en', 'es'] as const) {
      const html = decodeHtml(readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8'));
      const mainLabel = ui[lang]['nav.main'];
      const mobileLabel = ui[lang]['nav.mobile'];
      const footerLabel = ui[lang]['nav.footer'];

      expect(html).toContain(`aria-label="${mainLabel}"`);
      expect(html).toContain(`aria-label="${mobileLabel}"`);
      expect(html).toContain(`aria-label="${footerLabel}"`);

      expect(new Set([mainLabel, mobileLabel, footerLabel]).size).toBe(3);
    }
  });

  it.skipIf(!hasBuild)('renders a localized skip link in BaseLayout targeting #main-content', () => {
    for (const lang of ['pt', 'en', 'es'] as const) {
      const html = decodeHtml(readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8'));
      const expectedText = ui[lang]['a11y.skipToContent'];

      expect(html).toMatch(new RegExp(`<a[^>]+href="#main-content"[^>]*>\\s*${expectedText}\\s*<\\/a>`));
      expect(html).toContain('id="main-content"');
    }
  });
});
