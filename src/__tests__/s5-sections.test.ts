import { describe, it, expect } from 'vitest';
import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';
import cvData from '../../data/cv.json';
import { ui } from '../i18n/ui';

const root = resolve(__dirname, '../..');
const distDir = resolve(root, 'dist');
const hasBuild = existsSync(resolve(distDir, 'index.html'));

describe('S5 sections - cv.json requirements', () => {
  it('includes library and digital-image-processing in cv.json with pdf: false', () => {
    const library = cvData.projects.find(p => p.repo === 'github.com/thalesfb/library');
    expect(library, 'library project in cv.json').toBeDefined();
    expect(library?.pdf).toBe(false);
    expect(library?.technologies).toEqual(expect.arrayContaining(['Java', 'Spring Boot', 'MySQL']));
    expect(library?.description.pt).toBeTruthy();
    expect(library?.description.en).toBeTruthy();
    expect(library?.description.es).toBeTruthy();
    expect(library?.nameByLanguage?.pt).toBe('Sistema de Gerenciamento de Biblioteca');

    const dip = cvData.projects.find(p => p.repo === 'github.com/thalesfb/digital-image-processing');
    expect(dip, 'digital-image-processing project in cv.json').toBeDefined();
    expect(dip?.pdf).toBe(false);
    expect(dip?.technologies).toEqual(expect.arrayContaining(['Python', 'OpenCV', 'Jupyter', 'CI']));
    expect(dip?.description.pt).toBeTruthy();
    expect(dip?.description.en).toBeTruthy();
    expect(dip?.description.es).toBeTruthy();
    expect(dip?.nameByLanguage?.pt).toBe('Processamento Digital de Imagens');
  });

  it('includes services in cv.json with complete PT/EN/ES translations', () => {
    expect((cvData as any).services).toBeDefined();
    const services = (cvData as any).services;
    expect(Array.isArray(services)).toBe(true);
    expect(services.length).toBe(3);
    for (const service of services) {
      expect(service.id).toBeTruthy();
      expect(service.icon).toMatch(/^\/img\/icon-/);
      for (const lang of ['pt', 'en', 'es']) {
        expect(service.title[lang], `Missing service title in ${lang}`).toBeTruthy();
        expect(service.description[lang], `Missing service description in ${lang}`).toBeTruthy();
      }
    }
  });
});

describe('S5 sections - i18n requirements', () => {
  it('defines 6 nav items across all three languages', () => {
    for (const lang of ['pt', 'en', 'es'] as const) {
      expect(ui[lang]['nav.about']).toBeTruthy();
      expect(ui[lang]['nav.education']).toBeTruthy();
      expect(ui[lang]['nav.experience']).toBeTruthy();
      expect(ui[lang]['nav.projects']).toBeTruthy();
      expect(ui[lang]['nav.services']).toBeTruthy();
      expect(ui[lang]['nav.contact']).toBeTruthy();
    }
    expect(ui.pt['nav.about']).toBe('Sobre');
    expect(ui.pt['nav.education']).toBe('Formação');
    expect(ui.pt['nav.experience']).toBe('Experiência');
    expect(ui.pt['nav.projects']).toBe('Projetos');
    expect(ui.pt['nav.services']).toBe('Serviços');
    expect(ui.pt['nav.contact']).toBe('Contato');
  });

  it('defines accessible header aria-labels across all three languages', () => {
    for (const lang of ['pt', 'en', 'es'] as const) {
      expect((ui[lang] as any)['header.themeToggle']).toBeTruthy();
      expect((ui[lang] as any)['header.languageSelect']).toBeTruthy();
      expect((ui[lang] as any)['header.openMenu']).toBeTruthy();
      expect((ui[lang] as any)['header.closeMenu']).toBeTruthy();
    }
  });
});

describe('S5 sections - component architecture requirements', () => {
  it('Header removes search and provides aria-expanded on menu with 6 nav anchors', () => {
    const headerSource = readFileSync(resolve(root, 'src/components/Header.astro'), 'utf-8');
    expect(headerSource).not.toContain('search-input');
    expect(headerSource).not.toContain('search-toggle-mobile');
    expect(headerSource).not.toContain('mobile-search-bar');
    expect(headerSource).not.toContain('filterCards');

    expect(headerSource).toMatch(/id="hamburger"[^>]*aria-expanded="false"/);
    expect(headerSource).toMatch(/id="hamburger"[^>]*aria-controls="mobile-menu"/);

    // Nav has 6 anchors
    const anchorMatches = [...headerSource.matchAll(/href="(#(?:about|education|experience|projects|services|contact))"/g)].map(m => m[1]);
    const uniqueAnchors = [...new Set(anchorMatches)];
    expect(uniqueAnchors.sort()).toEqual(['#about', '#contact', '#education', '#experience', '#projects', '#services']);

    // Hash preservation on language switch
    expect(headerSource).toContain('window.location.hash');
  });

  it('Hero removes role rotation and cargo selector, fixing role to data-engineer', () => {
    const heroSource = readFileSync(resolve(root, 'src/components/Hero.astro'), 'utf-8');
    expect(heroSource).not.toContain('id="role-selector"');
    expect(heroSource).not.toContain('cv:role-change');
    expect(heroSource).not.toContain('rotateRole');
    expect(heroSource).not.toContain('data-roles=');
  });

  it('Experience component exists and renders CPEL and OPTIMIZR with green borders', () => {
    const expPath = resolve(root, 'src/components/Experience.astro');
    expect(existsSync(expPath), 'Experience.astro exists').toBe(true);
    const expSource = readFileSync(expPath, 'utf-8');
    expect(expSource).toContain('id="experience"');
    expect(expSource).toContain('border-brand-green');
    expect(expSource).toContain('cvData.experience');
    expect(expSource).toContain('exp.company');
  });

  it('Projects component renders static 3-col grid without carousel buttons or track', () => {
    const projSource = readFileSync(resolve(root, 'src/components/Projects.astro'), 'utf-8');
    expect(projSource).not.toContain('carousel-prev');
    expect(projSource).not.toContain('carousel-next');
    expect(projSource).not.toContain('carousel-track');
    expect(projSource).not.toContain('cv:role-change');
    expect(projSource).not.toContain('filterProjects');
    expect(projSource).toContain('grid-cols-1');
    expect(projSource).toContain('md:grid-cols-2');
    expect(projSource).toContain('xl:grid-cols-3');
  });

  it('Services component renders from cv.json without carousel and no hardcoded text', () => {
    const servSource = readFileSync(resolve(root, 'src/components/Services.astro'), 'utf-8');
    expect(servSource).not.toContain('carousel-prev');
    expect(servSource).not.toContain('carousel-next');
    expect(servSource).not.toContain('carousel-track');
    expect(servSource).not.toContain('Engenharia de Dados, BI e Machine Learning');
    expect(servSource).toContain('cvData.services');
    expect(servSource).toContain('grid-cols-1');
  });

  it('Lattes appears as social icon in Contact and text link in Footer, not separate line', () => {
    const contactSource = readFileSync(resolve(root, 'src/components/Contact.astro'), 'utf-8');
    expect(contactSource).toMatch(/aria-label="Currículo Lattes"/);
    expect(contactSource).toContain('>L<');

    const footerSource = readFileSync(resolve(root, 'src/components/Footer.astro'), 'utf-8');
    expect(footerSource).not.toContain('initCarousels');
    expect(footerSource).toContain('cvData.personal.lattes');

    const adr12 = readFileSync(resolve(root, 'docs/adr/0012-site-editorial-redesign.md'), 'utf-8');
    expect(adr12).not.toMatch(/Incluir Lattes no contato,/);
  });
});

describe('S5 sections - built output validation', () => {
  it.skipIf(!hasBuild)('verifies HTML output has no search, no carousel, no cv:role-change and 6 working anchors', () => {
    for (const lang of ['pt', 'en', 'es']) {
      const html = readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8');

      // Sem busca
      expect(html).not.toContain('search-input');
      expect(html).not.toContain('search-toggle-mobile');

      // Sem carrossel
      expect(html).not.toContain('carousel-prev');
      expect(html).not.toContain('carousel-next');
      expect(html).not.toContain('carousel-track');

      // Sem rotação de cargo
      expect(html).not.toContain('cv:role-change');
      expect(html).not.toContain('id="role-selector"');

      // Nav com 6 âncoras reais existentes
      for (const anchor of ['about', 'education', 'experience', 'projects', 'services', 'contact']) {
        expect(html, `missing anchor target id="${anchor}" in ${lang}`).toContain(`id="${anchor}"`);
      }

      // Experiência com CPEL e OPTIMIZR
      expect(html).toContain('CPEL');
      expect(html).toContain('OPTIMIZR');

      // Menu mobile com aria-expanded e aria-controls
      expect(html).toContain('aria-expanded="false"');
      expect(html).toContain('aria-controls="mobile-menu"');

      // Lattes uma vez no contato (ícone) e no rodapé
      const contactStart = html.indexOf('id="contact"');
      const contactSection = html.slice(contactStart, html.indexOf('</section>', contactStart));
      expect(contactSection).toContain('aria-label="Currículo Lattes"');
      expect(contactSection).toContain('>L<');

      const footerSection = html.slice(html.indexOf('<footer'));
      expect(footerSection).toContain('http://lattes.cnpq.br/9042504768658064');
    }
  });

  it.skipIf(!hasBuild)('verifies exact order and count of 7 projects on all routes', () => {
    for (const lang of ['pt', 'en', 'es']) {
      const html = readFileSync(resolve(distDir, lang, 'index.html'), 'utf-8');
      const projectsSection = html.slice(html.indexOf('id="projects"'), html.indexOf('id="services"'));

      const expectedRepos = [
        'github.com/thalesfb/ccw',
        'github.com/thalesfb/machine_learning',
        'github.com/thalesfb/library',
        'github.com/thalesfb/digital-image-processing',
        'github.com/thalesfb/AI',
      ];

      let lastIndex = -1;
      for (const repo of expectedRepos) {
        const idx = projectsSection.indexOf(repo);
        expect(idx, `Expected ${repo} in projects section of ${lang}`).toBeGreaterThan(-1);
        expect(idx, `Expected ${repo} to appear after previous project`).toBeGreaterThan(lastIndex);
        lastIndex = idx;
      }

      // 2 pesquisas IFC
      const p1Idx = projectsSection.indexOf(lang === 'pt' ? 'Infraestrutura de comunicação industrial' : lang === 'en' ? 'Industrial Communication Infrastructure' : 'Infraestructura de comunicación industrial');
      const p2Idx = projectsSection.indexOf(lang === 'pt' ? 'Plataforma de Decisão Compartilhada Humano-Máquina' : lang === 'en' ? 'Human-Machine Shared Decision Platform' : 'Plataforma de Decisión Compartida');
      expect(p1Idx).toBeGreaterThan(lastIndex);
      expect(p2Idx).toBeGreaterThan(p1Idx);

      // Excluded projects
      expect(projectsSection).not.toContain('Infrastructure & Web Services');
      expect(projectsSection).not.toContain('Data Structures');
    }
  });
});
