# ADR-0011: Geração dos PDFs do CV com Typst

## Status

Accepted

## Data

2026-11-19

## Contexto

O CV precisa ser atualizado nos idiomas português, inglês e espanhol sem editar manualmente documentos duplicados. O PDF anterior foi mantido com um modelo Word/DOCX, fontes e espaçamentos aprovados. O Google Docs e o Word são editores úteis para revisão, mas uma exportação dependente de editor, sistema operacional e fontes instaladas não oferece uma compilação reprodutível. A tentativa do PR #9 de preencher o DOCX com `data/cv.json` divergiu do PDF aprovado: perdeu acentos, omitiu o SENAI, inseriu métricas e tecnologias não aprovadas e produziu bullets vazios.

O documento aprovado usava Proxima Nova, indisponível sob licença livre adequada para distribuição junto ao repositório. A comparação de protótipos do S2 demonstrou que preservar a aparência do PDF antigo exige outra fonte e três páginas, enquanto o design clean com Inter atingiu duas páginas em cada idioma, coluna única, texto selecionável e links ativos. O Thales aprovou Typst como motor e o design clean com Inter.

## Opções debatidas

| Opção | Vantagens | Limites para este projeto |
|---|---|---|
| Typst | Compilação determinística, template declarativo, leitura nativa de JSON e binário disponível para CI Linux | O layout precisa ser mantido no template Typst; não reutiliza CSS do site |
| Chromium com HTML/CSS | Reutiliza padrões web e tem boa fidelidade visual | Exige browser e runtime maiores, consome mais memória e aumenta a superfície de versões |
| WeasyPrint | Usa HTML/CSS e suporta saída PDF em Linux | Requer runtime Python e dependências nativas; paginação e recursos precisam ser validados por plataforma |
| LibreOffice | Pode reutilizar DOCX e exporta sem interface gráfica | A renderização pode divergir do Word e depende de fontes, versão e configuração do escritório |

## Decisão

- Gerar os PDFs PT/EN/ES com Typst 0.15.1, chamando o compilador a partir de `scripts/build_cv_pdf.py`.
- Ler `data/cv.json` como única fonte de conteúdo. `cv/clean.typ` recebe o caminho dos dados e os parâmetros `lang` e `role` via `sys.inputs`.
- Usar o design clean de coluna única, duas páginas, com fontes Inter 400, 400 itálico, 600 e 700. Distribuir somente os arquivos de fonte sob SIL Open Font License e registrar a licença junto deles.
- Gerar a role `data-engineer` nos nomes de PDF já usados em `public/refs`.
- Por padrão, gravar em diretório temporário. Escrever em `public/refs` somente mediante `--publish-public-refs`; a CI sempre compila em diretório temporário e nunca publica ou commita PDFs.
- Remover o gerador DOCX/Word e seus testes. Manter `refs/template/*.docx` apenas como referência histórica, sem participação no processo.

## Critérios de fidelidade

Cada idioma precisa atender aos seguintes critérios antes de substituir os PDFs versionados:

1. Duas páginas em papel Letter.
2. Apenas as variantes da família Inter necessárias, incorporadas no PDF.
3. Texto extraído contém o conteúdo do JSON selecionado para o idioma e a role, inclusive bullets, projetos, skills, formação, certificações e idiomas; texto adicional é limitado aos rótulos de seção e à formatação determinística das datas.
4. Acentuação preservada e nenhum caractere de substituição U+FFFD.
5. Links `mailto:`, LinkedIn e GitHub presentes como anotações clicáveis.
6. Revisão visual página a página antes de publicar `public/refs`.

Testes locais de PDF podem indicar dependências Typst/Poppler ausentes e pular com mensagem clara. O CI instala versões e ferramentas fixadas e executa todos esses testes.

## Consequências

### Positivas

- Um único JSON alimenta o site e as três versões de PDF.
- O mesmo template gera idiomas e roles sem copiar o documento manualmente.
- Inter incorporada e ferramentas fixadas tornam as saídas reproduzíveis entre ambientes.
- O fluxo local e o CI têm proteção contra sobrescrita acidental dos PDFs públicos.

### Negativas

- O novo design não reproduz a tipografia Proxima Nova nem o leiaute anterior; os PDFs precisam de revisão editorial e visual.
- Mudanças longas no JSON podem exceder duas páginas e devem falhar na validação, sem encolher fonte ou omitir conteúdo automaticamente.
- A fonte e o Typst precisam permanecer fixados e licenciados junto à implementação.
- Os DOCX históricos deixam de ser atualizados pelo projeto.

## Referências

- `docs/proposals/0001-cv-pdf.md` — debate de opções e escolha do design clean
- `cv/clean.typ` — template Typst
- `scripts/build_cv_pdf.py` — compilador e proteção de publicação
- [Typst v0.15.1](https://github.com/typst/typst/releases/tag/v0.15.1)
- [Inter e licença SIL OFL](https://github.com/rsms/inter)
