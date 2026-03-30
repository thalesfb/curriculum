import { describe, it, expect } from 'vitest';
import cvData from '../../data/cv.json';

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
    }
  });
});
