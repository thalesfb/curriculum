import { describe, expect, it } from 'vitest';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

const root = resolve(__dirname, '../..');
const globalCss = readFileSync(join(root, 'src/styles/global.css'), 'utf8');
const baseLayout = readFileSync(join(root, 'src/layouts/BaseLayout.astro'), 'utf8');
const middleware = readFileSync(join(root, 'src/middleware.ts'), 'utf8');
const componentDir = join(root, 'src/components');
const componentFiles = readdirSync(componentDir)
  .filter(file => file.endsWith('.astro'))
  .map(file => ({ file, source: readFileSync(join(componentDir, file), 'utf8') }));

const themeBlock = globalCss.match(/@theme\s*\{([\s\S]*?)\n\}/)?.[1] ?? '';
const darkThemeBlock = globalCss.match(/\.dark\s*\{([\s\S]*?)\n\}/)?.[1] ?? '';

function tokenValue(block: string, token: string): string | undefined {
  return block.match(new RegExp(`${token}:\\s*(#[0-9a-fA-F]{6})\\s*;`))?.[1];
}

function luminance(hex: string): number {
  const channels = [1, 3, 5].map(offset => parseInt(hex.slice(offset, offset + 2), 16) / 255);
  const linear = channels.map(value => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
  return linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722;
}

function contrastRatio(foreground: string, background: string): number {
  const values = [luminance(foreground), luminance(background)].sort((a, b) => b - a);
  return (values[0] + 0.05) / (values[1] + 0.05);
}

describe('S5 design tokens and local fonts', () => {
  it('defines accessible text-on-brand and focus-ring values for both themes', () => {
    expect(tokenValue(themeBlock, '--color-text-on-brand')).toBe('#0F172A');
    expect(tokenValue(darkThemeBlock, '--color-text-on-brand')).toBe('#0F172A');
    expect(tokenValue(themeBlock, '--color-focus-ring')).toBe('#1D4ED8');
    expect(tokenValue(darkThemeBlock, '--color-focus-ring')).toBe('#60A5FA');

    expect(globalCss).toContain("--font-display: 'Libertinus Serif'");
    expect(globalCss).toContain('--font-body: system-ui');
    expect(globalCss).toContain("--font-code: 'Fira Code'");
  });

  it('keeps on-brand text contrast at or above 4.5:1 in both themes', () => {
    const lightText = tokenValue(themeBlock, '--color-text-on-brand');
    const lightBrand = tokenValue(themeBlock, '--color-brand-green');
    const darkText = tokenValue(darkThemeBlock, '--color-text-on-brand');
    const darkBrand = tokenValue(darkThemeBlock, '--color-brand-green');

    expect(lightText).toBeDefined();
    expect(lightBrand).toBeDefined();
    expect(darkText).toBeDefined();
    expect(darkBrand).toBeDefined();
    expect(contrastRatio(lightText!, lightBrand!)).toBeGreaterThanOrEqual(4.5);
    expect(contrastRatio(darkText!, darkBrand!)).toBeGreaterThanOrEqual(4.5);
  });

  it('declares local Libertinus and Fira Code font faces backed by files and OFL licenses', () => {
    const faces = [...globalCss.matchAll(/@font-face\s*\{([^}]+)\}/g)].map(([, block]) => block);
    const expectedFaces = [
      { family: 'Libertinus Serif', license: 'OFL-Libertinus.txt' },
      { family: 'Fira Code', license: 'OFL-FiraCode.txt' },
    ];

    for (const expected of expectedFaces) {
      const face = faces.find(block => block.includes(`font-family: '${expected.family}'`));
      expect(face, `${expected.family} @font-face`).toBeDefined();
      expect(face).toContain('font-display: swap');
      const files = [...face!.matchAll(/url\(['"]?([^)'"\s]+)['"]?\)/g)].map(([, url]) => url);
      expect(files.length).toBeGreaterThan(0);
      for (const file of files) {
        expect(existsSync(join(root, 'public', file.replace(/^\//, ''))), `${file} exists`).toBe(true);
      }
      const licensePath = join(root, 'public/fonts', expected.license);
      expect(existsSync(licensePath), `${expected.license} exists`).toBe(true);
      expect(readFileSync(licensePath, 'utf8')).toContain('SIL OPEN FONT LICENSE Version 1.1');
    }

    expect(baseLayout).toMatch(/rel="preload"[^>]*as="font"|as="font"[^>]*rel="preload"/);
    expect(baseLayout).toMatch(/href="\/fonts\/Libertinus[^\"]+"/);
  });

  it('does not load Google Fonts in the layout or generated pages', () => {
    expect(baseLayout).not.toMatch(/fonts\.(?:googleapis|gstatic)\.com/i);
    expect(baseLayout).not.toMatch(/Montserrat|Roboto/i);
    expect(globalCss).not.toMatch(/fonts\.(?:googleapis|gstatic)\.com|Montserrat|Roboto/i);
    expect(middleware).not.toMatch(/fonts\.(?:googleapis|gstatic)\.com/i);

    const dist = join(root, 'dist');
    if (existsSync(dist)) {
      const pages = ['pt', 'en', 'es'].map(lang => readFileSync(join(dist, lang, 'index.html'), 'utf8'));
      expect(pages.join('\n')).not.toMatch(/fonts\.(?:googleapis|gstatic)\.com/i);

      const cssDir = join(dist, '_astro');
      const generatedCss = readdirSync(cssDir)
        .filter(file => file.endsWith('.css'))
        .map(file => readFileSync(join(cssDir, file), 'utf8'))
        .join('\n');
      expect(generatedCss).toContain('--color-text-on-brand:#0f172a');
      expect(generatedCss).toContain('--color-focus-ring:#1d4ed8');
      expect(generatedCss).toMatch(/\.text-text-on-brand\{/);
    }
  });

  it('declares the color scheme used by the light and dark toggle', () => {
    expect(baseLayout).toMatch(/<meta name="color-scheme" content="light dark">/);
    const distPages = ['pt', 'en', 'es'].map(lang => join(root, 'dist', lang, 'index.html'));
    if (distPages.every(existsSync)) {
      for (const page of distPages) {
        expect(readFileSync(page, 'utf8')).toContain('<meta name="color-scheme" content="light dark">');
      }
    }
  });

  it('uses on-brand text for every green background and keeps visible focus outlines', () => {
    const visualFiles = [...componentFiles, { file: 'BaseLayout.astro', source: baseLayout }];
    for (const { file, source } of visualFiles) {
      const classValues = [...source.matchAll(/class=(?:"([^"]*)"|\{([^}]*)\})/gs)]
        .map(([, staticClasses, expression]) => staticClasses ?? expression ?? '');
      for (const classes of classValues.filter(value => /(?:^|\s)(?:[\w-]+:)*bg-brand-green(?:\s|$)/.test(value))) {
        expect(classes, `${file} green background`).not.toMatch(/\b(?:text-white|text-text-inverse|hover:text-white)\b/);
        if (classes.includes('inline-block h-3.5 w-3.5')) continue;
        expect(classes, `${file} green background uses on-brand text`).toMatch(/(?:^|\s)(?:[\w-]+:)*text-text-on-brand(?:\s|$)/);
      }
      expect(source, `${file} should use the global focus-visible ring`).not.toContain('outline-none');
    }

    expect(baseLayout).not.toContain('outline-none');
    expect(globalCss).toMatch(/:focus-visible\s*\{[^}]*outline:\s*2px solid var\(--color-focus-ring\)[^}]*outline-offset:\s*3px/s);
  });

  it('keeps the WhatsApp button fully opaque and disables motion for reduced-motion users', () => {
    const footer = componentFiles.find(({ file }) => file === 'Footer.astro')?.source ?? '';
    expect(footer).not.toMatch(/animate-pulse|opacity-30/);
    expect(globalCss).toMatch(/@media\s*\(prefers-reduced-motion:\s*reduce\)/);
    const reducedMotion = globalCss.match(/@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{([\s\S]*?)\n\}/)?.[1] ?? '';
    expect(reducedMotion).toMatch(/scroll-behavior:\s*auto/);
    expect(reducedMotion).toMatch(/animation:\s*none/);
    expect(reducedMotion).toMatch(/transition:\s*none/);
  });
});
