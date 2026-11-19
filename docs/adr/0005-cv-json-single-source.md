# ADR-0005: Dados do site e PDFs do CV em JSON

## Status

Accepted

## Data

2026-03-28

## Contexto

O portfólio exibe dados profissionais (experiência, projetos, skills, educação). Site e PDFs precisam consumir o conteúdo aprovado sem manter cópias editoriais divergentes.

## Decisão

Usar `data/cv.json` como fonte de conteúdo do site e entrada do gerador explícito de PDFs Typst. A geração local não publica arquivos automaticamente; substituir `public/refs` exige a flag explícita e revisão humana.

### Estrutura do JSON

```json
{
  "personal": { "name": "Thales Ferreira", ... },
  "summary": { "pt": "...", "en": "...", "es": "..." },
  "experience": [
    {
      "company": "...",
      "title": { "pt": "...", "en": "...", "es": "..." },
      "description": { "pt": "...", "en": "...", "es": "..." },
      "roles": ["data-engineer", "backend", "devops"]
    }
  ],
  "projects": [...],
  "skills": [...],
  "education": [...],
  "certifications": [...]
}
```

### Consumidores

1. **Astro Content Collections** — `file()` loader lê cv.json com validação Zod
2. **`cv/cv.typ`** — Formata o JSON com imprecv, multilíngue e filtrado pela role
3. **`scripts/build_cv_pdf.py`** — Chama Typst para gerar rascunhos e protege `public/refs` por padrão
4. **Figma i18n variables** — Textos do design espelham o JSON

### Geração dos PDFs

`cv/cv.typ` consome `data/cv.json` por caminho recebido via `sys.inputs`, usando o template imprecv 1.0.1 vendorizado sob Apache-2.0 e Libertinus Serif sob SIL Open Font License. O script Python usa Typst 0.15.1 com fontes locais e sistema de fontes desabilitado. O padrão grava em pasta temporária; publicar exige `--publish-public-refs`. A CI valida a geração em diretório temporário, sem publicar nem commitar PDFs. Os DOCX em `refs/template/` permanecem como referências históricas e não são entradas do gerador.

### Implementação atual (2026-11-19)

- `data/cv.json` alimenta o site e o gerador Typst dos PDFs.
- Os PDFs em `public/refs` são artefatos versionados de revisão humana; a CI não os altera.
- A saída local padrão é temporária; substituir `public/refs` precisa da flag `--publish-public-refs`.
- Os DOCX históricos não são lidos ou regravados pelo pipeline.

## Consequências

### Positivas

- Atualizar `data/cv.json` atualiza os consumidores que o leem; os PDFs aprovados exigem revisão separada
- Validação de schema com Zod em build time
- O gerador Typst produz PDFs multilíngues e filtrados por role em Linux, Windows e macOS com a mesma fonte embutida
- Testes de texto, paginação, fontes e links ajudam a detectar regressões antes da revisão visual
- Formato JSON é versionável (git diff legível)

### Negativas

- JSON grande pode ficar difícil de editar manualmente
- Sem UI de edição (precisa editar JSON direto)
- Alterar o conteúdo pode alterar quebras; cada PDF precisa passar pelos critérios de fidelidade e revisão humana antes da publicação

## Referências

- `data/cv.json` — Arquivo de dados
- `cv/cv.typ` — template imprecv localizado dos PDFs PT/EN/ES
- `scripts/build_cv_pdf.py` — geração explícita e validada dos PDFs
- `refs/template/*.docx` — referências históricas, fora do pipeline atual
