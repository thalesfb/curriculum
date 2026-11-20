import { describe, it, expect } from 'vitest';
import { existsSync, readFileSync, readdirSync } from 'fs';
import { resolve } from 'path';
import cvData from '../../data/cv.json';

const distDir = resolve(__dirname, '../../dist');
const hasBuild = existsSync(resolve(distDir, 'index.html'));
const decodeHtml = (html: string) => html
  .replace(/&amp;/g, '&')
  .replace(/&#39;|&#x27;/g, "'")
  .replace(/&quot;/g, '"');

describe('build output validation', () => {
  it.skipIf(!hasBuild)('generates /pt/index.html', () => {
    expect(existsSync(resolve(distDir, 'pt/index.html'))).toBe(true);
  });

  it.skipIf(!hasBuild)('generates /en/index.html', () => {
    expect(existsSync(resolve(distDir, 'en/index.html'))).toBe(true);
  });

  it.skipIf(!hasBuild)('generates /es/index.html', () => {
    expect(existsSync(resolve(distDir, 'es/index.html'))).toBe(true);
  });

  it.skipIf(!hasBuild)('PT page has lang="pt-BR"', () => {
    const html = readFileSync(resolve(distDir, 'pt/index.html'), 'utf-8');
    expect(html).toContain('lang="pt-BR"');
  });

  it.skipIf(!hasBuild)('EN page has lang="en"', () => {
    const html = readFileSync(resolve(distDir, 'en/index.html'), 'utf-8');
    expect(html).toContain('lang="en"');
  });

  it.skipIf(!hasBuild)('ES page has lang="es"', () => {
    const html = readFileSync(resolve(distDir, 'es/index.html'), 'utf-8');
    expect(html).toContain('lang="es"');
  });

  it.skipIf(!hasBuild)('pages contain Open Graph meta tags', () => {
    const html = readFileSync(resolve(distDir, 'pt/index.html'), 'utf-8');
    expect(html).toContain('og:title');
    expect(html).toContain('og:description');
    expect(html).toContain('og:image');
  });

  it.skipIf(!hasBuild)('pages contain hreflang tags', () => {
    const html = readFileSync(resolve(distDir, 'pt/index.html'), 'utf-8');
    expect(html).toContain('hreflang="pt"');
    expect(html).toContain('hreflang="en"');
    expect(html).toContain('hreflang="es"');
  });

  it.skipIf(!hasBuild)('sitemap was generated', () => {
    expect(existsSync(resolve(distDir, 'sitemap-index.xml'))).toBe(true);
  });

  it.skipIf(!hasBuild)('renders CV education and projects from JSON on all locale routes', () => {
    const unsupportedCredential = ['CC', 'NA'].join('');
    for (const lang of ['pt', 'en', 'es']) {
      const html = decodeHtml(readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8'));
      expect(html).not.toContain(unsupportedCredential);
      const senai = cvData.education.find(entry => entry.institution === 'SENAI' && entry.degree.pt === 'Operador de Computador');
      expect(html).toContain(senai?.degree[lang as 'pt' | 'en' | 'es']);
      const ifc = cvData.education.find(entry => entry.institution === 'Instituto Federal Catarinense');
      expect(html).toContain(ifc?.degree[lang as 'pt' | 'en' | 'es']);
      expect(html).toContain('2023–2026');
      expect(html).toContain('AWS Academy Cloud Architecting');
      expect(html).toContain(({ pt: 'Em curso', en: 'In progress', es: 'En curso' } as const)[lang as 'pt' | 'en' | 'es']);
      expect(html).toContain('data-roles=');
      expect(html).toContain('cv:role-change');
      for (const project of cvData.projects.filter(entry => [
        'Ensino Personalizado de Matemática: Oportunidades e Técnicas Computacionais',
        'Infraestrutura de comunicação industrial: implantação e integração de redes e protocolos para automação de processos',
        'Plataforma de Decisão Compartilhada Humano-Máquina para Processos Industriais',
      ].includes(entry.name))) {
        expect(html).toContain(project.nameByLanguage?.[lang as 'pt' | 'en' | 'es'] ?? project.name);
      }
    }
  });

  it.skipIf(!hasBuild)('does not expose an Optimizr location in the built locale pages', () => {
    for (const lang of ['pt', 'en', 'es']) {
      const html = decodeHtml(readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8'));
      expect(html).not.toContain('OPTIMIZR');
      expect(html).not.toMatch(/\b(?:Remoto|Remote)\b/);
    }
  });

  it.skipIf(!hasBuild)('separates About overview from responsive education and certification grids', () => {
    const html = readFileSync(resolve(distDir, 'pt/index.html'), 'utf-8');
    const overviewStart = html.indexOf('data-about-overview');
    const learningStart = html.indexOf('data-about-learning');
    expect(overviewStart).toBeGreaterThan(-1);
    expect(learningStart).toBeGreaterThan(overviewStart);

    const overview = html.slice(overviewStart, learningStart);
    expect(overview).toContain('id="about-summary"');
    expect(overview).not.toContain('data-education-grid');
    expect(overview).not.toContain('data-certifications-grid');
    const aboutEnd = html.indexOf('id="services"');
    const about = html.slice(overviewStart, aboutEnd);
    const educationGridStart = about.indexOf('data-education-grid');
    const certificationGridStart = about.indexOf('data-certifications-grid');
    expect(educationGridStart).toBeGreaterThan(-1);
    expect(educationGridStart).toBeLessThan(certificationGridStart);
    expect(about.indexOf('Formação')).toBeLessThan(about.indexOf('Certificações'));

    expect(about).toContain('xl:grid-cols-[3fr_2fr]');
    const educationGrid = about.slice(educationGridStart, about.indexOf('>', educationGridStart));
    const certificationGrid = about.slice(certificationGridStart, about.indexOf('>', certificationGridStart));
    for (const grid of [educationGrid, certificationGrid]) {
      expect(grid).toContain('grid-cols-1');
      expect(grid).toContain('md:grid-cols-2');
      expect(grid).toContain('xl:grid-cols-3');
    }
    expect(about).toContain('bg-bg-page');
    expect(about).not.toContain('bg-white');

    const astroAssets = resolve(distDir, '_astro');
    const css = readdirSync(astroAssets)
      .filter(file => file.endsWith('.css'))
      .map(file => readFileSync(resolve(astroAssets, file), 'utf-8'))
      .join('\n');
    expect(css).toContain('.dark');
    expect(css).toContain('--color-bg-page:#0f172a');
    expect(css).toContain('@media (width>=48rem)');
    expect(css).toContain('@media (width>=80rem)');
    expect(css).toMatch(/\.md\\:grid-cols-2\{grid-template-columns:repeat\(2,minmax\(0,1fr\)\)\}/);
    expect(css).toMatch(/\.xl\\:grid-cols-3\{grid-template-columns:repeat\(3,minmax\(0,1fr\)\)\}/);
    expect(css).toMatch(/\.xl\\:grid-cols-\\\[3fr_2fr\\\]\{grid-template-columns:3fr 2fr\}/);
  });
});
