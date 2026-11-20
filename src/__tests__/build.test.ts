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

  it.skipIf(!hasBuild)('renders grouped Alura cards and education without certification status', () => {
    const expectedHeadings = {
      pt: ['Formação', 'Certificações'],
      en: ['Education', 'Certifications'],
      es: ['Formación', 'Certificaciones'],
    } as const;
    const combinedHeadings = ['Educação & Certs', 'Education & Certs', 'Educación y Certs'];
    const pendingLabels = { pt: 'Em curso', en: 'In progress', es: 'En curso' } as const;

    for (const lang of ['pt', 'en', 'es'] as const) {
      const html = decodeHtml(readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8'));
      const learningStart = html.indexOf('data-about-learning');
      const learning = html.slice(learningStart, html.indexOf('id="services"', learningStart));
      const educationStart = learning.indexOf('data-education-grid');
      const certificationsStart = learning.indexOf('data-certifications-grid');
      const education = learning.slice(educationStart, certificationsStart);
      const certifications = learning.slice(certificationsStart);
      expect(learning.indexOf(expectedHeadings[lang][0])).toBeLessThan(learning.indexOf(expectedHeadings[lang][1]));
      for (const heading of combinedHeadings) expect(learning).not.toContain(heading);
      expect(html).not.toMatch(/Não informado|Not specified|No especificado|NÃ/);
      expect(education).not.toContain(pendingLabels[lang]);
      expect(certifications).toContain('AWS Academy Cloud Architecting');
      expect(certifications).toContain(pendingLabels[lang]);
      expect(education).toContain('data-education-period="2012"');
      expect(education).not.toContain('2012–2012');
    }

    const html = decodeHtml(readFileSync(resolve(distDir, 'pt/index.html'), 'utf-8'));
    const aboutStart = html.indexOf('data-about-learning');
    const aboutEnd = html.indexOf('id="services"', aboutStart);
    const certifications = html.slice(aboutStart, aboutEnd).split('data-certifications-grid')[1];
    expect(certifications).toContain('<details');
    expect(certifications).toContain('<summary');
    expect(certifications).toContain('data-alura-group');
    expect(certifications).toContain('Dados');
    expect(certifications).toContain('198h');
    expect(certifications).toContain('Modelagem de banco');
    expect(certifications).toContain('href="https://cursos.alura.com.br/user/thalesfb/fullCertificate/1ec4275c873ec751eabead5b304ef7f8"');
    expect(certifications).toContain('Latinoware 2014');
    expect(certifications.indexOf('AWS Academy Cloud Architecting')).toBeLessThan(certifications.indexOf('Imersão Engenharia de Software: Dev na Era da IA'));
    expect(certifications.indexOf('AWS Academy Graduate – Cloud Foundations')).toBeLessThan(certifications.indexOf('Imersão Engenharia de Software: Dev na Era da IA'));
    expect(certifications.lastIndexOf('Latinoware 2014')).toBeGreaterThan(certifications.indexOf('AWS Academy Graduate – Cloud Foundations'));
    expect(certifications.indexOf('AWS Academy Graduate – Cloud Foundations')).toBeLessThan(certifications.indexOf('UX & Design'));
    expect(certifications.indexOf('UX & Design')).toBeLessThan(certifications.indexOf('Latinoware 2025 (28h)'));
    expect(certifications.indexOf('Latinoware 2025 (28h)')).toBeLessThan(certifications.indexOf('Trilha Django REST Framework'));
    expect(certifications.indexOf('Trilha Django REST Framework')).toBeLessThan(certifications.indexOf('Dados'));
    expect(certifications.indexOf('Dados')).toBeLessThan(certifications.indexOf('Techstars Startup Weekend Videira 2025'));
  });


  it.skipIf(!hasBuild)('shows the Lattes profile link in every locale', () => {
    for (const lang of ['pt', 'en', 'es']) {
      const html = decodeHtml(readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8'));
      expect(html).toContain('href="http://lattes.cnpq.br/9042504768658064"');
      expect(html).toContain('>Lattes</a>');
    }
  });

});
