# ADR-0012: Redesign editorial do site

## Status

Accepted

## Data

2026-11-20

## Contexto

A auditoria do site encontrou diferenças entre as seções publicadas e o conteúdo aprovado em `data/cv.json`, controles e textos mantidos fora dessa fonte e uma hierarquia visual que não dá espaço suficiente aos blocos de conteúdo. O feedback do titular sobre a proposta anterior foi que ficou “tudo colado”. O PDF aprovado com o template imprecv (ADR-0011) oferece uma referência de hierarquia e respiro, mas precisa ser adaptado à leitura em telas.

A auditoria também identificou busca no header com comportamento inconsistente, rotação automática de cargo que altera conteúdo enquanto a pessoa lê, seções sem uma fonte única de dados e um botão flutuante de WhatsApp discreto demais e com pulso contínuo. O redesign deve preservar a arquitetura Astro, o CSS-first, o conteúdo multilíngue e as decisões de privacidade já registradas.

## Opções consideradas

| Opção | Direção | Vantagens | Limites |
|---|---|---|---|
| A | Editorial de engenharia, com serifas, entradas de experiência e timeline vertical | Aproxima o site da hierarquia editorial do PDF e destaca a trajetória | A timeline gráfica ocupa largura em telas pequenas; serifa no corpo prejudica a leitura longa |
| B | Caderno técnico, com rótulos monospace, linhas e módulos | Comunica engenharia e organiza competências de forma explícita | Pode parecer um dashboard e aumentar a densidade visual |
| C | Portfólio de casos, com projetos e resultados em destaque | Valoriza entregas verificáveis e links para código | Pode duplicar informações entre projetos, serviços e experiência |
| A modificada | Editorial de engenharia, com Libertinus apenas em display, entradas arejadas sem timeline gráfica e grades estáticas | Mantém a referência imprecv, melhora a leitura em telas e respeita a ordem do PDF | Exige revisão de títulos longos nos três idiomas e nos três breakpoints |

## Decisão

Adotar a opção A modificada, mantendo a implementação alinhada ao Figma (ADR-0004) antes de alterar os estilos do site:

- Hospedar Libertinus Serif localmente sob SIL Open Font License, reutilizando a distribuição licenciada em `cv/fonts/`. Usar WOFF2 se a conversão estiver disponível sem adicionar dependência; caso contrário, usar TTF da mesma distribuição. Aplicar a fonte somente a títulos e elementos display. Corpo e controles usam `system-ui`; não carregar fontes do Google.
- Apresentar experiência em blocos editoriais no estilo do imprecv, com cargo/organização, período e conteúdo bem espaçados. Não adicionar timeline gráfica.
- Ordenar Formação antes de Experiência, como no PDF aprovado e na ADR-0011.
- Manter Projetos e Serviços em grades estáticas, sem carrossel. Serviços permanecem e seus textos passam a vir de `data/cv.json` em PT/EN/ES.
- Remover a busca do header e a rotação automática de cargo; a pessoa escolhe o cargo manualmente.
- Manter o botão flutuante do WhatsApp totalmente opaco, sem animação de pulso.
- Manter Google Analytics conforme a ADR-0010.
- Propor no Figma os tokens semânticos `text/on-brand` e `focus-ring` para os temas claro e escuro. A validação visual e de contraste no Figma precede o mapeamento para CSS e Tailwind, conforme a ADR-0004.
- Usar `https://thalesfb.curriculum.optimizr.site` como domínio canônico documentado. `thales.optimizr.site` não resolve.

## Consequências

### Positivas

- O site e o PDF compartilham a ordem editorial e uma identidade tipográfica coerente, sem sacrificar legibilidade de texto longo na tela.
- Blocos com respiro, grades e controles manuais reduzem movimento e tornam a leitura previsível.
- Serviços e demais conteúdos permanecem alinhados ao JSON localizado.
- Tokens aprovados no Figma permitem contrastes e estados de foco consistentes entre temas.

### Negativas e riscos

- Libertinus precisa ser servida localmente e sua licença deve acompanhar os arquivos redistribuídos.
- A cópia atualmente vendorizada em `cv/fonts/` está em OTF; o primeiro PR deve confirmar uma conversão WOFF2 sem nova dependência ou obter o TTF equivalente da mesma distribuição OFL antes de configurar `@font-face`.
- Títulos e metadados em inglês e espanhol podem alterar a altura dos blocos e devem ser validados em 1440, 1024 e 375 px.
- A alteração do domínio canônico documentado não altera configuração de deploy; a configuração operacional deve ser verificada separadamente antes de qualquer publicação.

## Plano de implementação

1. **Tokens, tipografia e BaseLayout:** aprovar os estilos e tokens no Figma; hospedar a fonte local; mapear variáveis Figma para CSS custom properties e Tailwind; ajustar metadados e estrutura base. Testes Vitest cobrem tokens por tema, licença/arquivos locais, ausência de chamadas a fontes externas e estrutura do layout.
2. **Shell e conteúdo:** atualizar header, hero e seletor manual; consumir os textos de Serviços do JSON; renderizar Formação antes de Experiência em blocos editoriais e manter Projetos/Serviços em grades. Testes Vitest cobrem ordem, paridade PT/EN/ES, conteúdo derivado do JSON, controles manuais e ausência de carrossel.
3. **Acessibilidade, SEO, desempenho e documentação:** corrigir foco, contraste, labels e movimento reduzido; revisar metadados por idioma, imagens, fontes e JavaScript; atualizar as instruções e evidências visuais. Testes Vitest cobrem landmarks, links, metadados, JSON-LD e CSS de movimento reduzido; revisar build nas três rotas, temas e breakpoints.

Cada bloco depende da aprovação dos frames correspondentes no Figma antes da implementação visual. Não adicionar dependências sem decisão específica.

## Referências

- [ADR-0004 — Design System: Figma → Código](0004-design-system-figma-codigo.md)
- [ADR-0005 — Dados do CV como JSON](0005-cv-json-single-source.md)
- [ADR-0006 — Princípio KISS: HTML/CSS primeiro](0006-principio-kiss.md)
- [ADR-0010 — Google Analytics 4](0010-google-analytics.md)
- [ADR-0011 — Geração dos PDFs do CV com Typst](0011-geracao-pdf-cv-typst.md)
- [Guia do Design System no Figma](../guides/figma-design-system.md)
