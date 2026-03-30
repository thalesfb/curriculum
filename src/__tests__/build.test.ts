import { describe, it, expect } from 'vitest';
import { existsSync, readFileSync } from 'fs';
import { resolve } from 'path';

const distDir = resolve(__dirname, '../../dist');

describe('build output validation', () => {
  it.skipIf(!existsSync(distDir))('generates /pt/index.html', () => {
    expect(existsSync(resolve(distDir, 'pt/index.html'))).toBe(true);
  });

  it.skipIf(!existsSync(distDir))('generates /en/index.html', () => {
    expect(existsSync(resolve(distDir, 'en/index.html'))).toBe(true);
  });

  it.skipIf(!existsSync(distDir))('generates /es/index.html', () => {
    expect(existsSync(resolve(distDir, 'es/index.html'))).toBe(true);
  });

  it.skipIf(!existsSync(distDir))('PT page has lang="pt-BR"', () => {
    const html = readFileSync(resolve(distDir, 'pt/index.html'), 'utf-8');
    expect(html).toContain('lang="pt-BR"');
  });

  it.skipIf(!existsSync(distDir))('EN page has lang="en"', () => {
    const html = readFileSync(resolve(distDir, 'en/index.html'), 'utf-8');
    expect(html).toContain('lang="en"');
  });

  it.skipIf(!existsSync(distDir))('ES page has lang="es"', () => {
    const html = readFileSync(resolve(distDir, 'es/index.html'), 'utf-8');
    expect(html).toContain('lang="es"');
  });

  it.skipIf(!existsSync(distDir))('pages contain Open Graph meta tags', () => {
    const html = readFileSync(resolve(distDir, 'pt/index.html'), 'utf-8');
    expect(html).toContain('og:title');
    expect(html).toContain('og:description');
    expect(html).toContain('og:image');
  });

  it.skipIf(!existsSync(distDir))('pages contain hreflang tags', () => {
    const html = readFileSync(resolve(distDir, 'pt/index.html'), 'utf-8');
    expect(html).toContain('hreflang="pt"');
    expect(html).toContain('hreflang="en"');
    expect(html).toContain('hreflang="es"');
  });

  it.skipIf(!existsSync(distDir))('sitemap was generated', () => {
    expect(existsSync(resolve(distDir, 'sitemap-index.xml'))).toBe(true);
  });
});
