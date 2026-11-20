import { describe, it, expect } from 'vitest';
import { existsSync, readFileSync } from 'fs';
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
});
