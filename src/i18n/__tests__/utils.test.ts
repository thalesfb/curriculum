import { describe, it, expect } from 'vitest';
import { getLangFromUrl, useTranslations, useTranslatedPath } from '../utils';

describe('getLangFromUrl', () => {
  it('returns pt for /pt/ path', () => {
    expect(getLangFromUrl(new URL('https://example.com/pt/'))).toBe('pt');
  });

  it('returns en for /en/ path', () => {
    expect(getLangFromUrl(new URL('https://example.com/en/'))).toBe('en');
  });

  it('returns es for /es/ path', () => {
    expect(getLangFromUrl(new URL('https://example.com/es/'))).toBe('es');
  });

  it('returns default lang for unknown path', () => {
    expect(getLangFromUrl(new URL('https://example.com/fr/'))).toBe('pt');
  });

  it('returns default lang for root path', () => {
    expect(getLangFromUrl(new URL('https://example.com/'))).toBe('pt');
  });
});

describe('useTranslations', () => {
  it('returns PT translation for nav.home', () => {
    const t = useTranslations('pt');
    expect(t('nav.home')).toBe('Home');
  });

  it('returns EN translation for nav.about', () => {
    const t = useTranslations('en');
    expect(t('nav.about')).toBe('About');
  });

  it('returns ES translation for nav.contact', () => {
    const t = useTranslations('es');
    expect(t('nav.contact')).toBe('Contacto');
  });

  it('returns PT translation for hero.greeting', () => {
    const t = useTranslations('pt');
    expect(t('hero.greeting')).toBe('👋 Olá, eu sou Thales Ferreira');
  });

  it('returns EN translation for cta.download', () => {
    const t = useTranslations('en');
    expect(t('cta.download')).toBe('Download CV');
  });

  it('falls back to default lang for missing key', () => {
    const t = useTranslations('en');
    expect(t('nav.home')).toBe('Home');
  });
});

describe('useTranslatedPath', () => {
  it('prefixes path with /pt for Portuguese', () => {
    const translatePath = useTranslatedPath('pt');
    expect(translatePath('/')).toBe('/pt/');
  });

  it('prefixes path with /en for English', () => {
    const translatePath = useTranslatedPath('en');
    expect(translatePath('/')).toBe('/en/');
  });

  it('prefixes path with /es for Spanish', () => {
    const translatePath = useTranslatedPath('es');
    expect(translatePath('/')).toBe('/es/');
  });

  it('allows overriding the language', () => {
    const translatePath = useTranslatedPath('pt');
    expect(translatePath('/', 'en')).toBe('/en/');
  });
});
