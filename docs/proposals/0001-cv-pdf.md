# Proposta 0001: Geração dos PDFs do CV

## Objetivo

Atualizar os PDFs em português, inglês e espanhol a partir de `data/cv.json`, sem edição repetida e sem publicar uma saída antes da revisão do titular.

## Debate e decisão

Foram comparados Typst, Chromium com HTML/CSS, WeasyPrint e LibreOffice. Chromium requer browser/runtime maiores; WeasyPrint depende de bibliotecas nativas; LibreOffice mantém diferenças de renderização entre versões e ambientes. Typst oferece template declarativo, leitura nativa de JSON e compilação reproduzível em Linux.

Os documentos aprovados usavam Proxima Nova e eram mantidos em Word/Google Docs. O preenchimento automático tentado no PR #9 perdeu acentos, omitiu o SENAI, inseriu dados sem aprovação e gerou bullets vazios. O design clean com Inter foi posteriormente rejeitado pelo Thales porque o espaçamento ficou “tudo colado”.

A decisão atual é usar Typst com o template `imprecv` 1.0.1 do Typst Universe, sob Apache-2.0, com a atribuição preservada em `cv/vendor/imprecv/`. O layout mantém nome centralizado, contatos separados, seções com régua e espaço entre entradas; Formação aparece antes de Experiência, conforme a ordem editorial do basic-resume. A fonte escolhida é Libertinus Serif, distribuída localmente sob SIL OFL 1.1 para compilação determinística e sem rede.

## Escopo da solução

- `data/cv.json` continua sendo a única fonte de conteúdo factual.
- `cv/cv.typ` recebe `path`, `lang` e `role` via `sys.inputs` e filtra o conteúdo pela role.
- `scripts/build_cv_pdf.py` usa Typst 0.15.1, `cv/fonts` e Poppler para validar páginas, fontes, texto, acentos e links.
- `--font-path cv/fonts --ignore-system-fonts` asseguram o uso da família local.
- A geração padrão grava em pasta temporária. `public/refs` só é substituída com `--publish-public-refs` e revisão humana.
- CI executa geração e validação em pasta temporária; não publica nem commita PDFs.
- Os DOCX permanecem apenas como referência histórica.

## Critérios de revisão

- Duas páginas Letter por idioma quando o texto couber com o espaçamento do imprecv; admite-se até três páginas para preservar o respiro sem eliminar conteúdo ou diminuir fonte, com justificativa na revisão.
- Apenas fontes Libertinus Serif incorporadas.
- Conteúdo extraído corresponde ao JSON localizado e filtrado para `data-engineer`; somente rótulos das seções e datas podem ser formatados pelo template.
- Acentos, links ativos e providers válidos preservados; placeholders de provider ocultos.
- Revisão visual página a página antes de aceitar os PDFs versionados.

Detalhes e consequências estão em [ADR-0011](../adr/0011-geracao-pdf-cv-typst.md).
