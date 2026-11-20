# ADR-0011: Geração dos PDFs do CV com Typst

## Status

Accepted

## Data

2026-11-19

## Contexto

O currículo precisa ser atualizado em português, inglês e espanhol sem editar documentos duplicados. Os PDFs aprovados usavam Proxima Nova e eram mantidos em Word/Google Docs; a exportação dependia do editor, do sistema operacional e das fontes disponíveis. A tentativa do PR #9 de preencher o DOCX com `data/cv.json` divergiu do conteúdo aprovado, perdeu acentos, omitiu o SENAI, incluiu dados sem aprovação e gerou bullets vazios.

A escolha anterior de layout clean com Inter foi rejeitada pelo titular porque o resultado ficou visualmente “tudo colado”. O pacote `imprecv` do Typst Universe tem espaçamento e hierarquia visual mais próximos da referência selecionada. A ordem de experiência do pacote não atende à preferência editorial; este projeto coloca Formação antes de Experiência, como no template basic-resume. A tipografia do modelo original não pode ser redistribuída com segurança como fonte livre.

## Opções debatidas

| Opção | Vantagens | Limites para este projeto |
|---|---|---|
| Typst | Compilação determinística, template declarativo, leitura nativa de JSON e binário instalável no CI | O layout precisa permanecer no template Typst |
| Chromium com HTML/CSS | Reutiliza padrões web e permite visual familiar | Exige browser/runtime maiores, consome mais memória e amplia a superfície de versões |
| WeasyPrint | Usa HTML/CSS e gera PDF em Linux | Requer runtime Python e dependências nativas; paginação precisa ser validada por plataforma |
| LibreOffice | Pode abrir DOCX e exportar sem interface gráfica | A renderização diverge entre versões e depende de fontes e configuração do escritório |

## Decisão

- Gerar os PDFs PT/EN/ES com Typst 0.15.1 por `scripts/build_cv_pdf.py`, lendo `data/cv.json` via os inputs `path`, `lang` e `role`.
- Vendorizar `imprecv` 1.0.1 em `cv/vendor/imprecv/`, sob Apache-2.0, incluindo licença e aviso de atribuição. Não depender de import remoto em build.
- Adotar as regras visuais do imprecv: nome centralizado em caixa alta, título, contatos separados por losangos, títulos de seção em caixa alta com régua, datas alinhadas à direita e espaçamento entre entradas. Ordem: Sumário, Formação, Experiência, Projetos, Competências, Certificações e Idiomas.
- Usar Libertinus Serif, com arquivos locais e licença SIL Open Font License 1.1 em `cv/fonts/`. Compilar com `--font-path cv/fonts --ignore-system-fonts`; remover os arquivos Inter.
- Gerar a role `data-engineer` nos nomes atuais em `public/refs`.
- A saída padrão é temporária. Só substituir `public/refs` com `--publish-public-refs`, após revisar os PDFs; CI gera artefatos temporários e nunca publica nem commita PDFs.
- Remover o gerador Word/DOCX e seus testes. Manter `refs/template/*.docx` apenas como referência histórica.

## Critérios de fidelidade

1. Papel Letter e duas páginas quando o conteúdo cabe com o espaçamento do modelo; admite-se até três páginas quando necessário para não comprimir fonte, remover conteúdo ou reduzir o respiro, com justificativa registrada na revisão.
2. Somente variantes Libertinus Serif incorporadas no PDF.
3. Texto extraído corresponde ao JSON localizado e filtrado para a role, exceto rótulos de seção e formatação determinística de datas. Não exibir providers ausentes ou placeholders “Não informado”, “Not specified” e “No especificado”.
4. Acentos preservados, sem U+FFFD.
5. Links mailto, LinkedIn e GitHub mantidos como anotações clicáveis.
6. Revisão visual página a página antes de publicar em `public/refs`.

Os testes locais podem pular a integração PDF com mensagem clara quando Typst/Poppler não estiverem instalados. O CI fixa Typst e instala Poppler para executar esses testes.

## Consequências

### Positivas

- Um JSON alimenta o site e os três PDFs sem edição manual repetida.
- O pacote e a fonte são locais, licenciados e reproduzíveis sem rede durante a compilação.
- O espaçamento e a ordem das seções atendem à decisão editorial aprovada.
- A proteção do gerador evita sobrescrever PDFs públicos sem opt-in.

### Negativas

- O layout escolhido não reproduz a Proxima Nova nem o documento Word original.
- Conteúdo futuro pode exigir uma terceira página; não se reduz tipografia ou conteúdo automaticamente.
- O projeto deve preservar as atribuições Apache-2.0 e OFL junto aos arquivos de terceiros.
- Os DOCX históricos não são atualizados pelo projeto.

## Referências

- `docs/proposals/0001-cv-pdf.md` — comparação e decisão do template
- `cv/cv.typ` — template localizado, com Formação antes de Experiência
- `cv/vendor/imprecv/` — fonte do template e atribuição Apache-2.0
- `cv/fonts/` — Libertinus Serif e licença SIL OFL 1.1
- `scripts/build_cv_pdf.py` — compilador e proteção de publicação
- [Typst v0.15.1](https://github.com/typst/typst/releases/tag/v0.15.1)
- [imprecv 1.0.1](https://github.com/jskherman/imprecv), licenciado sob Apache-2.0
