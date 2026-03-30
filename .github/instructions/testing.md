# Testing Instructions

## TDD — Test-Driven Development (MANDATORY)

This project follows strict TDD. The cycle is:

```
RED    → Write a failing test first
GREEN  → Write the minimum code to make it pass
REFACTOR → Clean up without breaking tests
```

### Rules

1. **NEVER write production code without a failing test first**
2. Write only enough test to fail (one assertion at a time)
3. Write only enough code to pass the failing test
4. Refactor only when all tests are green
5. Run tests after every change

### Workflow

```bash
# 1. Write test
npm run test        # RED - test fails

# 2. Implement
npm run test        # GREEN - test passes

# 3. Refactor
npm run test        # Still GREEN - safe to commit
```

## Test Stack

| Type | Tool | What to test |
| ---- | ---- | ------------ |
| Unit | Vitest | Utility functions, i18n helpers, data transforms |
| Component | Vitest + Testing Library | Astro components render correctly |
| Build | `npm run build` | No build errors, all pages generated |
| Lighthouse | Chrome DevTools | Performance > 95, Accessibility > 95, SEO > 95 |
| Links | `npx linkinator` | No broken links |
| HTML | W3C Validator | Valid HTML5 |

## What to test (TDD)

| Feature | Test first |
| ------- | ---------- |
| i18n helper `useTranslations()` | Returns correct string for locale |
| CV data loader | Parses cv.json, filters by role |
| Dark mode toggle | Adds/removes `.dark` class, persists in localStorage |
| WhatsApp link builder | Generates correct `wa.me` URL per language |
| Contact form validation | Validates required fields, email format |
| Page generation | `/pt/`, `/en/`, `/es/` all render with correct lang attr |

## Example TDD cycle

```typescript
// 1. RED - test first
// src/i18n/__tests__/utils.test.ts
import { useTranslations } from '../utils';

test('returns PT translation for nav.home', () => {
  const t = useTranslations('pt');
  expect(t('nav.home')).toBe('Home');
});

test('returns EN translation for nav.about', () => {
  const t = useTranslations('en');
  expect(t('nav.about')).toBe('About');
});

// 2. GREEN - implement minimum code
// src/i18n/utils.ts
export function useTranslations(lang: string) {
  return (key: string) => ui[lang][key];
}

// 3. REFACTOR - add types, handle missing keys
```

## Checklist before deploy

- [ ] All tests pass (`npm run test`)
- [ ] `npm run build` succeeds
- [ ] All 3 languages render (`/pt/`, `/en/`, `/es/`)
- [ ] Dark mode toggle works and persists
- [ ] WhatsApp button links correctly
- [ ] Contact form submits
- [ ] Responsive on 375px, 1024px, 1440px
- [ ] Lighthouse all green (> 95)
- [ ] No console errors
