# ADR-0012: Evolução visual do site

## Status

Accepted

## Data

2026-11-20

## Contexto

A direção editorial criada do zero foi rejeitada porque removia elementos que dão identidade ao site atual. A decisão aprovada é evoluir o layout existente com correções: preservar a hierarquia, a foto, os cards e os elementos de marca, ao mesmo tempo que se adicionam Experiência, dados completos e tipografia local. O conteúdo continua vindo de `data/cv.json` (ADR-0005), e o sistema visual segue Figma → CSS custom properties → Tailwind (ADR-0004).

O PDF com imprecv (ADR-0011) é uma referência para Libertinus Serif e legibilidade, não para substituir o layout do site por blocos sem cards. A auditoria também identificou busca no header e rotação automática de cargo que distraem a leitura, além de necessidade de melhorar o contraste de texto em botões de marca.

## Opções consideradas

| Opção | Direção | Avaliação |
|---|---|---|
| A | Editorial do zero, inspirado no PDF | Rejeitada: retirava foto, ícones, logos, tags, CTA e rodapé escuro do layout aprovado. |
| B | Caderno técnico com módulos, linhas e rótulos monospace | Não escolhida: alteraria a linguagem visual e aumentaria a densidade. |
| C | Portfólio de casos com projetos como destaque principal | Não escolhida: reorganizaria o site e poderia duplicar conteúdo entre projetos, serviços e experiência. |
| Layout atual com correções | Preservar a identidade existente, corrigir conteúdo e controles e acrescentar as seções aprovadas | Escolhida pelo titular e validada no Figma v2. |

## Decisão

Manter a linguagem visual atual e aplicar as seguintes mudanças aprovadas:

- Preservar o Hero com foto, cards com borda verde, ícones de serviços, tags com ícone, logos de marca, botão **Contratar**, rodapé escuro e botão flutuante do WhatsApp. O WhatsApp fica com 100% de opacidade e sem pulso.
- Usar Libertinus Serif self-hosted sob SIL OFL nos títulos H1/H2/H3. Usar stack `system-ui` no corpo e controles. Usar Fira Code self-hosted sob SIL OFL nas tags. Não usar Google Fonts.
- Adicionar a seção **Experiência** em cards depois de **Sobre**. Formação permanece dentro de Sobre e vem antes de Experiência.
- Exibir Formação e Certificações completas com logos. Formação: IFC, SENAI 2013, Mater Salvatoris e SENAI 2012. Certificações: AWS Cloud Architecting em andamento, grupos Alura (403h), AWS Cloud Foundations, Latinoware, Techstars, DO188 e RH294. Alura usa `<details>/<summary>` para expandir seus nove grupos.
- Exibir Projetos e Serviços em grades, sem carrossel e sem filtro por cargo. Os textos de Serviços permanecem em `data/cv.json` nas três línguas. O site usa a role fixa `data-engineer`; não há seletor de role.
- Manter Google Analytics conforme ADR-0010.
- Usar a união dos projetos selecionados no Figma anterior com os projetos de `data/cv.json`, ordenada por evidência de atividade (commits) e qualidade/completude do README no GitHub. A ordem aprovada é: (1) TCC `ccw` — 257 commits; (2) `machine_learning` — 107; (3) `library` — 91, Java/Spring; (4) `digital-image-processing` — 40, README detalhado e CI; (5) `AI`; (6–7) os dois projetos de pesquisa do IFC. `infra_web` (9 commits e README vazio) e `Data-Structure` (README vazio) ficam fora. Conteúdo e descrições publicados continuam sujeitos ao JSON e às evidências dos repositórios.
- Incluir Lattes somente como ícone social com o glifo visual “L” (junto a LinkedIn, GitHub e Instagram) e no rodapé, sem linha separada no contato.
- Remover busca do header e rotação automática de cargo.
- Criar os tokens Theme `text/on-brand: #0F172A` nos dois temas e `focus-ring: #1D4ED8` no tema claro / `#60A5FA` no escuro. O Figma é a fonte dos tokens; mapear para CSS e Tailwind conforme ADR-0004.
- Usar `https://thalesfb.curriculum.optimizr.site` como domínio canônico documentado. `thales.optimizr.site` não resolve.

## Consequências

### Positivas

- O redesign preserva elementos reconhecíveis e corrige problemas de conteúdo sem recomeçar a interface.
- A experiência profissional e os dados completos passam a compor a navegação do currículo com conteúdo centralizado em `data/cv.json`.
- Tipografia auto-hospedada e tokens semânticos mantêm controle local e coerência entre os temas.
- Grades estáticas e role fixa deixam todo o conteúdo visível sem carrossel, busca ou mudança automática durante a leitura.

### Negativas e riscos

- Libertinus Serif e Fira Code precisam ser servidas localmente com as licenças SIL OFL correspondentes.
- A cópia Libertinus atualmente vendorizada em `cv/fonts/` está em OTF; a implementação deve confirmar conversão WOFF2 sem nova dependência ou usar TTF equivalente da mesma distribuição OFL.
- A lista completa de formação, certificações e projetos aumenta o comprimento da página e precisa ser revisada em 1440, 1024 e 375 px nos dois temas.
- Alterar documentação do domínio não altera configuração operacional de deploy; validar essa configuração separadamente antes de qualquer publicação.

## Plano de implementação

1. **Tokens, tipografia e shell:** aplicar no código os valores e estilos do Figma v2; preservar Hero, navegação e botões; fixar role em `data-engineer`; remover busca/rotação. Testes Vitest cobrem tokens por tema, arquivos/fontes locais, ausência de fontes externas e estrutura das três rotas.
2. **Conteúdo e seções:** renderizar formação e certificações completas dentro de Sobre, Alura expansível, Experiência em cards e Projetos/Serviços em grade, com todos os projetos e sem filtro de role. Testes Vitest cobrem conteúdo e ordenação vindos do JSON, links/Lattes, logos, ausência de carrossel/filtro e paridade PT/EN/ES.
3. **Acessibilidade, SEO e desempenho:** validar contraste, foco, labels, navegação por teclado, metadados, imagens e movimento reduzido. Testes Vitest cobrem landmarks, metadados por idioma, JSON-LD, foco/labels e redução de movimento; revisar build nos três breakpoints e dois temas.

## Referências

- [ADR-0004 — Design System: Figma → Código](0004-design-system-figma-codigo.md)
- [ADR-0005 — Dados do CV como JSON](0005-cv-json-single-source.md)
- [ADR-0006 — Princípio KISS: HTML/CSS primeiro](0006-principio-kiss.md)
- [ADR-0010 — Google Analytics 4](0010-google-analytics.md)
- [ADR-0011 — Geração dos PDFs do CV com Typst](0011-geracao-pdf-cv-typst.md)
- [Guia do Design System no Figma](../guides/figma-design-system.md)
