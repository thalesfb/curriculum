import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

const root = resolve(__dirname, '../..');
const css = readFileSync(resolve(root, 'src/styles/global.css'), 'utf-8');
const header = readFileSync(resolve(root, 'src/components/Header.astro'), 'utf-8');

describe('type scale after the S5 font switch', () => {
  it('normalizes the x-height of the display serif so headings keep their visual size', () => {
    expect(css).toMatch(/\.font-display\s*\{[^}]*font-size-adjust:\s*0\.5\d*/);
  });

  it('normalizes the x-height of the system-ui body text', () => {
    expect(css).toMatch(/body\s*\{[^}]*font-size-adjust:\s*0\.5\d*/);
  });
});

describe('header layout without search', () => {
  it('centers the desktop nav links between brand and actions', () => {
    expect(header).toMatch(/class="hidden lg:flex flex-1 justify-center items-center/);
  });

  it('no longer pushes the actions with ml-auto', () => {
    expect(header).not.toMatch(/class="ml-auto hidden lg:flex/);
  });
});
