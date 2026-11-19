# Proposta 0001: Geração dos PDFs do CV

## Objetivo

Atualizar os PDFs em português, inglês e espanhol a partir de `data/cv.json`, sem edição manual repetida e sem publicar uma saída antes da revisão do titular.

## Debate e escolha

Foram comparados Typst, Chromium com HTML/CSS, WeasyPrint e LibreOffice. Chromium poderia compartilhar padrões web, mas adiciona o browser e maior consumo de recursos. WeasyPrint requer runtime Python e dependências nativas. LibreOffice permitiria reaproveitar DOCX, mas mantém diferenças de renderização entre versões e ambientes. Typst oferece template declarativo, leitura nativa de JSON e execução reprodutível em Linux.

O modelo anterior tinha Proxima Nova e era editado/exportado por Word ou Google Docs. O preenchimento automático tentado no PR #9 não preservou o documento aprovado: perdeu acentos, omitiu o SENAI, incluiu dados sem aprovação e gerou bullets vazios. Copiar o layout antigo com uma fonte substituta continuaria preso a três páginas e a métricas tipográficas diferentes.

O protótipo comparou um modo próximo ao modelo anterior com várias fontes livres e um modo clean com Inter. A decisão aprovada pelo Thales foi Typst com Inter OFL e design clean de coluna única, legível por ATS, com duas páginas, texto selecionável e links ativos.

## Escopo da solução

- `data/cv.json` continua sendo a fonte única do conteúdo factual.
- `cv/clean.typ` renderiza idioma e role recebidos por parâmetro.
- O script Python usa Typst 0.15.1, fonte local e Poppler para validar paginação, fontes, texto, acentos e anotações.
- A geração padrão grava em diretório temporário. `public/refs` só é substituída com `--publish-public-refs` e revisão humana.
- A CI executa a geração e validação em pasta temporária; não publica nem commita PDFs.
- Os arquivos DOCX permanecem apenas como referência histórica.

## Critérios de revisão

- Exatamente duas páginas Letter por idioma.
- Apenas fontes Inter incorporadas.
- Conteúdo extraído corresponde ao JSON localizado e filtrado para `data-engineer`; somente rótulos de seção e datas podem ser formatados pelo template.
- Acentos e links ativos preservados.
- Revisão visual de ambas as páginas em cada idioma antes de aceitar os PDFs versionados.

Detalhes, trade-offs e consequências estão em [ADR-0011](../adr/0011-geracao-pdf-cv-typst.md).
