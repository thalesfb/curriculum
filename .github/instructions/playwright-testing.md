# Playwright Testing Instructions

## Setup

Playwright skill está em `~/.claude/skills/playwright-skill/`.

```bash
# Setup (primeira vez)
cd ~/.claude/skills/playwright-skill && npm run setup
```

## Execução

```bash
# Rodar script de teste
cd ~/.claude/skills/playwright-skill && node run.js /tmp/playwright-test-*.js

# Inline rápido
cd ~/.claude/skills/playwright-skill && node run.js "
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.goto('file:///c:/dev/curriculum/index.html');
await page.screenshot({ path: '/tmp/screenshot.png', fullPage: true });
await browser.close();
"
```

## Padrão de teste visual (QA)

Scripts sempre em `/tmp/playwright-test-*.js`, nunca no projeto.

```javascript
// /tmp/playwright-test-responsive.js
const { chromium } = require('playwright');
const path = require('path');

const TARGET_URL = 'file:///' + path.resolve('c:/dev/curriculum/index.html').replace(/\\/g, '/');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const viewports = [
    { name: 'desktop', width: 1440, height: 900 },
    { name: 'tablet', width: 1024, height: 768 },
    { name: 'mobile', width: 375, height: 812 },
  ];

  for (const vp of viewports) {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.goto(TARGET_URL, { waitUntil: 'networkidle' });
    await page.screenshot({ path: `/tmp/${vp.name}.png`, fullPage: true });
    console.log(`📸 ${vp.name} saved`);
  }

  // Dark mode
  await page.evaluate(() => document.documentElement.classList.add('dark'));
  await page.screenshot({ path: '/tmp/desktop-dark.png', fullPage: true });

  await browser.close();
})();
```

## Playwright CLI (microsoft/playwright-cli)

Para testes interativos e debugging, usar o Playwright CLI:

```bash
# Instalar globalmente
npm i -g playwright-cli

# Abrir browser interativo (inspect mode)
npx playwright open http://localhost:4321

# Abrir com device emulation
npx playwright open --device="iPhone 13" http://localhost:4321
npx playwright open --device="iPad Pro 11" http://localhost:4321

# Gerar código (codegen) — grava interações e gera script
npx playwright codegen http://localhost:4321

# Screenshot via CLI
npx playwright screenshot http://localhost:4321 /tmp/screenshot.png
npx playwright screenshot --full-page http://localhost:4321 /tmp/full.png

# Gerar PDF
npx playwright pdf http://localhost:4321 /tmp/page.pdf

# Instalar browsers
npx playwright install chromium
npx playwright install firefox
npx playwright install webkit
```

### Codegen — gravar testes automaticamente

```bash
# Abre browser e grava todas as interações como script
npx playwright codegen http://localhost:4321

# Com viewport específico
npx playwright codegen --viewport-size=375,812 http://localhost:4321

# Salvar diretamente em arquivo
npx playwright codegen -o /tmp/recorded-test.js http://localhost:4321
```

### Device emulation útil para o projeto

```bash
# Mobile (375px - mesmo do Figma)
npx playwright open --device="iPhone 13" http://localhost:4321

# Tablet (1024px - mesmo do Figma)
npx playwright open --device="iPad Pro 11" http://localhost:4321

# Desktop (1440px)
npx playwright open --viewport-size=1440,900 http://localhost:4321
```

## Checklist de QA visual

Ao rodar testes Playwright, verificar:

- [ ] Header sticky funciona ao scrollar
- [ ] Dark mode toggle alterna corretamente
- [ ] Logo clicável scrolla ao topo
- [ ] Menu hamburger abre/fecha no mobile
- [ ] Carrosséis scrollam horizontalmente
- [ ] WhatsApp FAB visível com animação pulse
- [ ] WhatsApp FAB fica nítido no hover
- [ ] Formulário de contato tem campos e botão
- [ ] Todos os 3 breakpoints (1440, 1024, 375) renderizam
- [ ] Foto de perfil carrega
- [ ] Logos de educação carregam (IFC, SENAI, Alura, Red Hat, AWS)
- [ ] Botão Baixar CV aponta para PDF correto

## Rules

- Scripts de teste vão em `/tmp/` — nunca no projeto
- Usar `headless: true` para CI, `headless: false` para debug local
- Screenshots salvos em `/tmp/` para comparação
- URL parametrizada no topo do script (`TARGET_URL`)
- Para dev server Astro: `http://localhost:4321`
- Para HTML estático: `file:///c:/dev/curriculum/index.html`
