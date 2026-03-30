# Guia Prático: Design System no Figma

**Projeto:** Portfolio Thales Ferreira — thales.optimizr.site
**Figma:** `UXq2erOANKQqaWegZQ9nk1`
**Autor:** Thales Ferreira | Assistido por Claude Code

---

## Sumário

1. [Estrutura do Arquivo](#1-estrutura-do-arquivo)
2. [Variáveis e Tokens](#2-variáveis-e-tokens)
3. [Auto Layout e Responsividade](#3-auto-layout-e-responsividade)
4. [Componentização](#4-componentização)
5. [Prototyping e Interações](#5-prototyping-e-interações)
6. [Dark Mode com Variáveis](#6-dark-mode-com-variáveis)
7. [i18n com Variable Modes](#7-i18n-com-variable-modes)
8. [Lições Aprendidas](#8-lições-aprendidas)

---

## 1. Estrutura do Arquivo

### Páginas

| Página | Propósito |
|--------|-----------|
| **Design** | Frames de todos os dispositivos (Desktop 1440px, Tablet 1024px, Mobile 375px, Menu Overlay) |
| **Components** | Todos os componentes master — nunca instâncias aqui |
| **Style Guide** | Referência visual de tipografia, cores, ícones |

### Regra de ouro

> Componentes vivem APENAS na página Components.
> A página Design usa APENAS instâncias.
> Isso garante que qualquer alteração no master propague para todas as instâncias.

### Frames de dispositivo

```
Design/
├── Desktop (1440 x auto) — Layout completo, vertical auto layout
├── Tablet (1024 x auto)  — Adaptação, não apenas redução
├── Mobile (375 x auto)   — Mobile-first para interações touch
└── Mobile Menu (Open) (375 x 526) — Overlay do menu expandido
```

Cada frame usa **Auto Layout Vertical** com `itemSpacing: 0` para as seções se empilharem. O header é filho fixo (`numberOfFixedChildren = 1`) — posicionado como último child do frame, com `constraints: STRETCH horizontal`.

---

## 2. Variáveis e Tokens

### Coleções de Variáveis

O projeto usa **3 coleções** de variáveis, cada uma representando uma **dimensão ortogonal** (nunca misture dimensões na mesma coleção):

| Coleção | Tipo | Modos | Propósito |
|---------|------|-------|-----------|
| **Theme** | COLOR | Light / Dark | Cores semânticas que mudam com o tema |
| **i18n** | STRING | PT / EN / ES | Textos da interface traduzidos |
| **Role** | STRING | Data Engineer / Backend / DevOps / Management | Variantes de cargo profissional |

### Theme — Variáveis de Cor (17 variáveis)

#### Backgrounds

| Variável | Light | Dark | Uso |
|----------|-------|------|-----|
| `bg/page` | `#F8FAFC` | `#0F172A` | Fundo geral da página |
| `bg/card` | `#FFFFFF` | `#1E293B` | Superfícies de cards |
| `bg/section-alt` | `#F8FAFC` | `#142032` | Seções alternadas |
| `bg/dark` | `#334155` | `#081020` | Seções escuras (contato) |
| `bg/input` | `#F8FAFC` | `#1E293B` | Campos de formulário |

#### Textos

| Variável | Light | Dark | Uso |
|----------|-------|------|-----|
| `text/primary` | `#0F172A` | `#F1F5F9` | Títulos, texto principal |
| `text/secondary` | `#64748B` | `#94A3B8` | Descrições, subtextos |
| `text/inverse` | `#F1F5F9` | `#F1F5F9` | Texto sobre fundo escuro |
| `text/placeholder` | `#64748B` | `#94A3B8` | Placeholders de input |

#### Marca e Acentos

| Variável | Light | Dark | Uso |
|----------|-------|------|-----|
| `brand/green` | `#059669` | `#34D399` | CTAs, bordas, ícone `>_` |
| `border/line` | `#E2E8F0` | `#334155` | Divisores, bordas de input |

### Como aplicar variáveis

1. Selecione o elemento
2. Clique no campo de cor (fill ou stroke)
3. Clique no ícone de variável (hexágono)
4. Selecione a variável semântica

**Nunca use cores hardcoded.** Sempre vincule a uma variável. Isso garante que o dark mode funcione automaticamente.

### Arquitetura de variáveis — Por que semântico?

```
ERRADO:  Texto usa #0F172A (hex fixo)
         → No dark mode, continua preto sobre fundo preto

CORRETO: Texto usa text/primary (variável)
         → Light: #0F172A (preto sobre branco)
         → Dark:  #F1F5F9 (branco sobre preto escuro)
```

### Scoping de variáveis

Cada variável deve ter seu **escopo** limitado:
- Variáveis de cor: escopo `FILL_COLOR` e `STROKE_COLOR`
- Variáveis de número (spacing): escopo `GAP` e `PADDING`
- Isso evita que variáveis de cor apareçam em pickers de número e vice-versa

---

## 3. Auto Layout e Responsividade

### Conceitos fundamentais

| Propriedade | Quando usar | Exemplo no projeto |
|-------------|-------------|-------------------|
| **Hug Contents** | Container adapta ao conteúdo | Botões, badges, tags de tech |
| **Fill Container** | Elemento ocupa espaço disponível | Textos em cards, barra de pesquisa |
| **Fixed** | Dimensão imutável | Ícones 48px, foto de perfil, logos |

### Regra crítica

> Se qualquer filho usa **Fill**, o pai automaticamente muda de Hug para Fixed naquele eixo.

### Padrão de seção do projeto

```
[VERTICAL, FILL width, HUG height, padding 64-80]
└── Section
    ├── [HORIZONTAL, FILL width] Title + Nav Arrows
    ├── [HORIZONTAL, FILL width, clip, overflow-x] Content (carousel)
    │   ├── Card 1 (FIXED width)
    │   ├── Card 2 (FIXED width)
    │   └── Card 3 (FIXED width)
```

### Header fixo (sticky)

No Figma, "Fix position when scrolling" funciona via `numberOfFixedChildren`:

1. O header deve ser o **último child** do frame (children fixos ficam no final)
2. O frame pai define `numberOfFixedChildren = 1`
3. O header usa `layoutPositioning: ABSOLUTE` com `constraints: STRETCH horizontal`
4. Adicione **transparência no fill** (opacity 0.9) para efeito glassmorphism
5. **Compense o espaço** adicionando padding-top no primeiro conteúdo igual à altura do header

```
Frame (overflow: VERTICAL, numberOfFixedChildren: 1)
├── hero (paddingTop: 194 = 100 original + 94 header)
├── about
├── ...
└── header ← ÚLTIMO child, ABSOLUTE, STRETCH
```

### Carrosséis

O padrão de carrossel no projeto:

```
Container (HORIZONTAL, clipsContent: true, overflowDirection: HORIZONTAL)
├── Card 1 (FIXED width)
├── Card 2 (FIXED width)
└── Card 3 (FIXED width)
```

**Desktop/Tablet:** Mostram N cards + setas de navegação (componente Button Arrow)
**Mobile:** Mostram 1 card + peek do próximo (swipe nativo, sem setas)

Dimensionamento dos cards por breakpoint:

| Breakpoint | Seção | Largura card | Visíveis |
|------------|-------|-------------|----------|
| Desktop 1440px | O que eu faço | ~400px | 3 (sem carousel) |
| Desktop 1440px | Projetos | ~280px | 4 + peek |
| Tablet 1024px | O que eu faço | 364px | 2 + peek |
| Tablet 1024px | Projetos | ~280px | 3 + peek |
| Mobile 375px | O que eu faço | 290px | 1 + peek |
| Mobile 375px | Projetos | 280px | 1 + peek |

### Textos em cards — regra FILL

> Textos dentro de cards **DEVEM** usar `layoutSizingHorizontal: FILL`.
> Nunca use largura fixa em textos — eles estourarão o card em breakpoints menores.

---

## 4. Componentização

### Componentes do projeto

| Componente | Tipo | Variantes | Página |
|------------|------|-----------|--------|
| **Button** | Component Set | Filled / Outline | Components |
| **Button Arrow** | Component Set | Active / Inactive | Components |
| **Theme Toggle** | Component Set | State=Light / State=Dark | Components |
| **Tech Tag** | Component | — | Components |
| **Input Field** | Component | — | Components |
| **Social Icon Button** | Component | — | Components |
| **Section Title** | Component | — | Components |
| **Nav Link** | Component | — | Components |
| **Card Service** | Component | — | Components |
| **Card Project** | Component | — | Components |

### Component Sets vs Components simples

- **Component Set** (variant container): Quando o componente tem **estados visuais diferentes** (hover, active, light/dark, filled/outline)
- **Component simples**: Quando é um elemento reutilizável sem variantes

### Criando um Component Set (exemplo: Button Arrow)

1. Crie 2 Components separados: `State=Active` e `State=Inactive`
2. Selecione ambos → `Combine as Variants`
3. O Figma cria automaticamente a property `State` com valores `Active` e `Inactive`
4. Nas instâncias, troque o estado pelo painel de propriedades

### Boas práticas de componentização

1. **Nomeação:** Use `/` para agrupar → `Button/Filled`, `Button/Outline`
2. **Nunca edite instâncias para mudar estrutura** — edite o master
3. **Fills e strokes devem usar variáveis** — não cores hardcoded
4. **Ícones dentro de componentes:** Se o ícone muda entre instâncias, use **Instance Swap property**
5. **Textos editáveis:** Exponha como **Text property** para edição sem deep-click

### Estados do Button Arrow

```
State=Active:
  - Fill: bg/card (branco light, cinza dark)
  - Stroke: brand/green (verde)
  - Arrow stroke: text/primary (escuro light, claro dark)

State=Inactive:
  - Fill: bg/card (opacity 0.5)
  - Stroke: text/secondary (opacity 0.4)
  - Arrow stroke: text/secondary (opacity 0.4)
```

**Uso:** Na primeira posição do carrossel, seta esquerda = Inactive (não pode voltar), seta direita = Active.

---

## 5. Prototyping e Interações

### Tipos de interação usados

| Interação | Trigger | Ação | Exemplo |
|-----------|---------|------|---------|
| **Scroll to section** | ON_CLICK | SCROLL_TO | Menu links → seções |
| **Navigate** | ON_CLICK | NAVIGATE | Hamburger → Menu Overlay |
| **Change to** | ON_CLICK | CHANGE_TO | Theme Toggle Light ↔ Dark |
| **Set Variable Mode** | ON_CLICK | SET_VARIABLE_MODE | Theme toggle muda modo Dark |

### Menu mobile — fluxo completo

```
Mobile: Hamburger (ON_CLICK) → NAVIGATE → "Mobile Menu (Open)" (slide left)
Menu:   Close X (ON_CLICK) → NAVIGATE → "Mobile" (slide right)
Menu:   Nav items (ON_CLICK) → SCROLL_TO → seção correspondente
```

### Theme Toggle — Component Set interativo

1. Componente tem 2 variantes: `State=Light` e `State=Dark`
2. Cada variante tem reação `ON_CLICK`:
   - `CHANGE_TO` → alterna para a outra variante
   - `SET_VARIABLE_MODE` → muda o modo da coleção Theme

**Importante:** Para o SET_VARIABLE_MODE funcionar no Play mode, os frames **não podem ter modo explícito definido**. Use `clearExplicitVariableModeForCollection()` em todos os frames.

### Logo como scroll-to-top

Todos os logos (nav-brand no desktop/tablet, logo-icon no mobile) têm reação:
```
ON_CLICK → SCROLL_TO → hero frame (transition: null)
```

---

## 6. Dark Mode com Variáveis

### Como funciona

1. A coleção **Theme** tem 2 modos: Light e Dark
2. Cada variável define um valor para cada modo
3. Ao mudar o modo, **todos os elementos bindados mudam automaticamente**

### Checklist de dark mode

- [ ] Todos os fills de texto usam `text/primary` ou `text/secondary`
- [ ] Todos os fundos usam `bg/page`, `bg/card`, `bg/section-alt`
- [ ] Bordas usam `border/line`
- [ ] Ícones vetoriais (fills/strokes) usam variáveis de cor
- [ ] Logos de marcas (IFC, SENAI, Alura, Red Hat, AWS) **mantêm cores originais** — NÃO tematizar
- [ ] Botões outline: fill com opacity 0, stroke com `brand/green`
- [ ] Contraste WCAG mínimo 4.5:1 para texto, 3:1 para elementos grandes

### Erros comuns no dark mode

| Erro | Causa | Solução |
|------|-------|---------|
| Texto invisível | Fill hardcoded preto | Bindar a `text/primary` |
| Ícone sumiu | Fill/stroke sem variável | Bindar a variável semântica |
| Logo perdeu identidade | Tematizou logo de marca | Manter cores originais |
| Toggle não funciona no Play | Frame tem modo explícito | `clearExplicitVariableModeForCollection()` |
| Contraste ruim | Cores claras sobre fundo claro | Ajustar valores da variável no modo Dark |

---

## 7. i18n com Variable Modes

### Estrutura da coleção i18n

A coleção **i18n** contém variáveis STRING com 3 modos: PT, EN, ES.

Exemplo:
```
nav/home:    PT="Home"    EN="Home"     ES="Inicio"
nav/about:   PT="Sobre"   EN="About"    ES="Acerca"
nav/services: PT="Serviços" EN="Services" ES="Servicios"
hero/greeting: PT="Olá, eu sou" EN="Hi, I'm" ES="Hola, soy"
```

### Seletor de idioma visual

O header de cada dispositivo contém um `lang-selector` com:
- Ícone de globo (círculo + meridiano + equador)
- Label "PT" (texto)
- Seta dropdown (chevron)

No código, esse seletor abrirá opções PT/EN/ES que mudam o modo da coleção i18n.

### Cuidados com i18n

1. **Texto em alemão é ~30% mais longo** que em inglês — use FILL nos textos
2. **Nunca concatene strings traduzidas** — use chaves completas
3. **Acentuação:** Sempre usar acentos corretos (Serviços, Portfólio, Educação)

---

## 8. WhatsApp Button (ADR-0008)

### Component Set

| Variante | Opacidade | Quando |
|----------|-----------|--------|
| `State=Default` | 30% | Estado padrão — sutil, não atrapalha conteúdo |
| `State=Hover` | 100% | Desktop: mouse hover. Mobile: ao tocar |

### Interação

- **Desktop:** `ON_HOVER` → `CHANGE_TO` State=Hover (dissolve 0.3s)
- **Mobile/Tablet:** Ao clicar redireciona direto para WhatsApp

### Especificações

| Propriedade | Valor |
|-------------|-------|
| Tamanho | 56x56px (mesmo em todos os devices) |
| Border radius | 28px (circular) |
| Cor | WhatsApp Green `#25D366` |
| Ícone | SVG oficial WhatsApp (28x28px, branco) |
| Sombra | `0 4px 12px rgba(0,0,0,0.25)` |
| Posição | Fixed, bottom-right, acima do footer |
| Z-index | Acima do conteúdo, abaixo do header |

### Link por idioma

| Idioma | Mensagem pré-determinada |
|--------|--------------------------|
| PT | `Olá Thales! Vi seu portfólio e gostaria de conversar sobre um projeto.` |
| EN | `Hi Thales! I saw your portfolio and would like to discuss a project.` |
| ES | `Hola Thales! Vi tu portafolio y me gustaría conversar sobre un proyecto.` |

URL base: `https://wa.me/5549998048695?text=...`

### Implementação CSS (pulsar)

No código, o botão terá animação CSS de pulsar para chamar atenção periodicamente:

```css
.whatsapp-fab {
  animation: pulse 3s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.05); }
}
.whatsapp-fab:hover {
  animation: none;
  opacity: 1;
  transform: scale(1.1);
}
```

---

## 9. Lições Aprendidas

### O que deu certo

1. **Variáveis semânticas desde o início** — dark mode funcionou com poucos ajustes
2. **Component Sets para estados** — Button Arrow Active/Inactive, Theme Toggle
3. **Carrossel com overflow horizontal** — padrão escalável para qualquer quantidade de cards
4. **Header fixo via numberOfFixedChildren** — funciona no protótipo e mapeia direto para CSS `position: sticky`

### O que deu errado e como corrigimos

1. **Fills hardcoded** — Vários ícones tinham cores fixas que sumiram no dark mode → Auditoria e binding em massa
2. **Spacers vazios com HUG** — Frames sem filhos com `layoutSizingVertical: HUG` colapsam para 0px → Usar FIXED ou padding do container
3. **Textos com largura fixa em cards** — Overflow em breakpoints menores → Sempre usar FILL
4. **Modo explícito nos frames** — Bloqueava SET_VARIABLE_MODE no protótipo → Limpar modos explícitos
5. **Componentes fora da página Components** — Button Arrow estava "solto" → Mover/recriar na página correta

### Regras para manutenção

1. Qualquer novo componente vai para a página **Components**
2. Qualquer nova cor vai como **variável na coleção Theme**
3. Qualquer novo texto de UI vai como **variável na coleção i18n**
4. Teste dark mode após qualquer alteração visual
5. Verifique todos os 3 breakpoints após mudanças de layout
