import { describe, it, expect } from 'vitest';
import { ui, languages, defaultLang, showDefaultLang } from '../ui';

describe('ui.ts data integrity', () => {
  it('exports all three languages', () => {
    expect(Object.keys(languages)).toEqual(['pt', 'en', 'es']);
  });

  it('defaultLang is pt', () => {
    expect(defaultLang).toBe('pt');
  });

  it('showDefaultLang is true', () => {
    expect(showDefaultLang).toBe(true);
  });

  it('all languages have the same keys as defaultLang', () => {
    const ptKeys = Object.keys(ui.pt).sort();
    const enKeys = Object.keys(ui.en).sort();
    const esKeys = Object.keys(ui.es).sort();
    expect(enKeys).toEqual(ptKeys);
    expect(esKeys).toEqual(ptKeys);
  });

  it('no translation value is empty string', () => {
    for (const [lang, translations] of Object.entries(ui)) {
      for (const [key, value] of Object.entries(translations)) {
        expect(value, `${lang}.${key} is empty`).not.toBe('');
      }
    }
  });

  it('has at least 20 translation keys', () => {
    expect(Object.keys(ui.pt).length).toBeGreaterThanOrEqual(20);
  });

  it('localizes formal education and certification subsection headings', () => {
    expect([
      ui.pt['about.education.formal'],
      ui.en['about.education.formal'],
      ui.es['about.education.formal'],
    ]).toEqual(['Formação', 'Education', 'Formación']);
    expect([
      ui.pt['about.certifications'],
      ui.en['about.certifications'],
      ui.es['about.certifications'],
    ]).toEqual(['Certificações', 'Certifications', 'Certificaciones']);
  });
});
