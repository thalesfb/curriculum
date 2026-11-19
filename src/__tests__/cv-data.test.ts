import { describe, it, expect } from 'vitest';
import cvData from '../../data/cv.json';
import { ui } from '../i18n/ui';

const LANGUAGES = ['pt', 'en', 'es'];
const ROLES = ['data-engineer', 'backend', 'devops', 'management', 'frontend'];

describe('cv.json schema validation', () => {
  it('has meta section with required fields', () => {
    expect(cvData.meta).toBeDefined();
    expect(cvData.meta.version).toMatch(/^\d+\.\d+\.\d+$/);
    expect(cvData.meta.languages).toEqual(LANGUAGES);
    expect(cvData.meta.roles).toEqual(ROLES);
  });

  it('has personal section with required fields', () => {
    expect(cvData.personal.name).toBeTruthy();
    expect(cvData.personal.email).toMatch(/@/);
    expect(cvData.personal.phone).toBeTruthy();
    expect(cvData.personal.linkedin).toBeTruthy();
    expect(cvData.personal.github).toBeTruthy();
  });

  it('personal.location has all languages', () => {
    for (const lang of LANGUAGES) {
      expect((cvData.personal.location as Record<string, string>)[lang]).toBeTruthy();
    }
  });

  it('uses the approved contact email', () => {
    expect(cvData.personal.email).toBe('thalesfb15@gmail.com');
  });

  it('personal.titles covers all roles and languages', () => {
    for (const role of ROLES) {
      const titles = cvData.personal.titles as Record<string, Record<string, string>>;
      expect(titles[role]).toBeDefined();
      for (const lang of LANGUAGES) {
        expect(titles[role][lang], `Missing title for ${role}/${lang}`).toBeTruthy();
      }
    }
  });

  it('summary covers all roles and languages', () => {
    for (const role of ROLES) {
      const summary = cvData.summary as Record<string, Record<string, string>>;
      expect(summary[role]).toBeDefined();
      for (const lang of LANGUAGES) {
        expect(summary[role][lang], `Missing summary for ${role}/${lang}`).toBeTruthy();
      }
    }
  });

  it('keeps unsupported cost metrics out of every summary', () => {
    for (const summaries of Object.values(cvData.summary)) {
      for (const summary of Object.values(summaries)) {
        expect(summary).not.toMatch(/70\s*%/i);
      }
    }
  });

  it('keeps approved Portuguese accents in education and summaries', () => {
    expect(cvData.education.map(entry => entry.degree.pt)).toContain('Bacharelado em Ciência da Computação');
    expect(ui.pt['cv.education']).toContain('FORMAÇÃO');
    expect(cvData.summary['data-engineer'].pt).toContain('atuação de ponta a ponta');
  });

  it('has the approved IFC period without a status label', () => {
    const ifc = cvData.education.find(entry => entry.institution === 'Instituto Federal Catarinense');
    expect(ifc?.period).toEqual({ start: '2023-02', end: '2026-12' });
    expect(ifc).not.toHaveProperty('status');
  });

  it('includes both approved SENAI courses', () => {
    const senai = cvData.education.filter(entry => entry.institution === 'SENAI');
    expect(senai.map(entry => entry.degree.pt)).toEqual([
      'Aprendizagem Industrial de Suporte e Manutenção em Microcomputadores e Redes Locais',
      'Operador de Computador',
    ]);
  });

  it('preserves confirmed skills and language proficiency', () => {
    expect(cvData.skills['languages-backend'].items).toEqual(expect.arrayContaining(['Java', 'Spring Boot']));
    expect(cvData.skills['ml-data'].items).toEqual(expect.arrayContaining(['Scikit-learn', 'XGBoost', 'TensorFlow']));
    expect(cvData.skills.frontend.items).toEqual(expect.arrayContaining(['React', 'TypeScript']));
    expect(cvData.languages.map(entry => [entry.language.pt, entry.level.pt])).toEqual([
      ['Português', 'Nativo'],
      ['Inglês', 'Intermediário'],
      ['Espanhol', 'Intermediário'],
    ]);
  });

  it('includes all approved LinkedIn certifications', () => {
    const names = cvData.certifications.map(certification => certification.name.pt);
    for (const name of [
      'Excel com IA',
      'Imersão Engenharia de Software: Dev na Era da IA',
      'AWS Academy Graduate – Cloud Foundations',
      'Django REST Framework',
      'Git e GitHub',
      'Latinoware 2025 (28h)',
      'Techstars Startup Weekend Videira 2025',
    ]) {
      expect(names).toContain(name);
    }
  });

  it('keeps the three locale translations for approved CV fields', () => {
    for (const entry of cvData.education) {
      for (const lang of LANGUAGES) expect(entry.degree[lang]).toBeTruthy();
    }
    for (const entry of cvData.certifications) {
      for (const lang of LANGUAGES) expect(entry.name[lang]).toBeTruthy();
    }
    for (const entry of cvData.experience) {
      for (const lang of LANGUAGES) {
        expect(entry.role[lang]).toBeTruthy();
        for (const bullet of entry.bullets) expect(bullet[lang]).toBeTruthy();
      }
    }
  });

  it('keeps literal CMAQ and TBC descriptions and the approved CPEL title', () => {
    const cmaq = cvData.experience.find(entry => entry.company === 'CMAQ');
    const tbc = cvData.experience.find(entry => entry.company === 'TBC NETWORK EIRELI');
    const cpel = cvData.experience.find(entry => entry.company === 'CPEL');
    expect(cmaq?.bullets[0].pt).toBe('Gerenciei estoque e controle de mercadorias, implementando melhorias nos processos de cadastro e atendimento ao cliente.');
    expect(tbc?.bullets[0].pt).toBe('Realizei manutenção de equipamentos de redes e análise de tráfego, garantindo infraestrutura eficiente.');
    expect(cpel?.role.pt).toBe('Full Stack Data Engineer with Software and DevOps Expertise');
  });

  it('retains every approved PDF bullet for Optimizr and CPEL', () => {
    const opt = cvData.experience.find(entry => entry.company === 'OPTIMIZR');
    const cpel = cvData.experience.find(entry => entry.company === 'CPEL');
    expect(opt?.bullets.map(bullet => bullet.pt)).toEqual(expect.arrayContaining([
      'Liderei a consultoria em TI, abrangendo o desenvolvimento de programas de computador customizáveis e sob encomenda, web design, suporte técnico e tratamento de dados.',
      'Criei relatórios digitais que integraram métricas de qualidade, elevando significativamente os padrões de produção.',
      'Elaborei dashboards avançados em Power BI para análise de tendências e suporte à alta gestão.',
      'Atuei na preparação de documentos e serviços especializados de apoio administrativo, e ofereci treinamento em informática.',
    ]));
    expect(cpel?.bullets.map(bullet => bullet.pt)).toEqual(expect.arrayContaining([
      'Desenvolvi um sistema de controle de produção que otimizou a eficiência operacional e reduziu desperdícios.',
      'Criei relatórios digitais que integraram métricas de qualidade, aumentando significativamente os padrões de produção.',
      'Implementei processos analíticos para monitoramento de energia gerada pela usina hidrelétrica, apoiando decisões estratégicas.',
      'Desenvolvi dashboards avançados em Power BI para análise de tendências e suporte à alta gestão.',
      'Projetei um software de gestão integrada, otimizando fluxos de trabalho e comunicação entre setores.',
    ]));
  });

  it('every experience entry has required fields', () => {
    for (const exp of cvData.experience) {
      expect(exp.company).toBeTruthy();
      expect(exp.period.start).toMatch(/^\d{4}-\d{2}$/);
      for (const lang of LANGUAGES) {
        expect((exp.role as Record<string, string>)[lang], `Missing role ${lang} for ${exp.company}`).toBeTruthy();
        expect((exp.location as Record<string, string>)[lang], `Missing location ${lang} for ${exp.company}`).toBeTruthy();
      }
    }
  });

  it('every project has required fields in all languages', () => {
    for (const proj of cvData.projects) {
      expect(proj.name).toBeTruthy();
      expect(proj.repo).toBeTruthy();
      expect(proj.technologies.length).toBeGreaterThan(0);
      for (const lang of LANGUAGES) {
        expect((proj.description as Record<string, string>)[lang], `Missing description ${lang} for ${proj.name}`).toBeTruthy();
      }
      if (proj.nameByLanguage) {
        for (const lang of LANGUAGES) expect(proj.nameByLanguage[lang]).toBeTruthy();
      }
    }
  });

  it('keeps the IFC capstone project title and translations', () => {
    const project = cvData.projects.find(entry => entry.name === 'Ensino Personalizado de Matemática: Oportunidades e Técnicas Computacionais');
    expect(project?.repo).toBe('github.com/thalesfb/ccw');
    expect(project?.nameByLanguage).toEqual({
      pt: 'Ensino Personalizado de Matemática: Oportunidades e Técnicas Computacionais',
      en: 'Personalized Mathematics Teaching: Opportunities and Computational Techniques',
      es: 'Enseñanza Personalizada de Matemáticas: Oportunidades y Técnicas Computacionales',
    });
  });
});
