# ADR-0005: Dados do site e rascunhos de CV em JSON

## Status

Accepted

## Data

2026-03-28

## Contexto

O portfolio exibe dados profissionais (experiência, projetos, skills, educação). O site e os PDFs publicados precisam manter fontes de conteúdo aprovadas e a apresentação visual existente.

## Decisão

Usar `data/cv.json` como fonte de conteúdo do site e como entrada de rascunhos de PDF. Os PDFs publicados são artefatos aprovados e não são automaticamente regenerados a partir do JSON.

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
2. **`scripts/generate_cv_pdfs.py`** — Gera rascunhos de PDF a partir do JSON e do DOCX via Microsoft Word no Windows
3. **Figma i18n variables** — Textos do design espelham o JSON

### PDFs com layout fixo

O arquivo `refs/template/curriculo_thales_ferreira_pt.docx` é apenas a entrada do gerador atual; não reproduz o conteúdo aprovado dos PDFs publicados. A geração é uma operação local explícita: o padrão grava em pasta temporária. Substituir `public/refs` exige `--output-dir public/refs --publish-public-refs`, revisão humana e aprovação do conteúdo. A CI Linux e o build Astro não executam o gerador.

### Implementação atual (2026-11-19)

- `data/cv.json` alimenta o site e pode alimentar rascunhos do gerador; ainda não está alinhado ao conteúdo aprovado dos PDFs.
- Os PDFs em `public/refs` são a fonte aprovada do conteúdo publicado do currículo.
- Não há gerador de variantes Markdown nem diretório `output/` versionado neste repositório.

## Consequências

### Positivas

- Atualizar `data/cv.json` atualiza os consumidores que o leem; os PDFs aprovados exigem revisão separada
- Validação de schema com Zod em build time
- O gerador de PDF permite produzir rascunhos locais a partir do DOCX
- Formato JSON é versionável (git diff legível)

### Negativas

- JSON grande pode ficar difícil de editar manualmente
- Sem UI de edição (precisa editar JSON direto)

## Referências

- `data/cv.json` — Arquivo de dados
- `refs/template/curriculo_thales_ferreira_pt.docx` — entrada do gerador de rascunhos, não fonte aprovada dos PDFs
- `scripts/generate_cv_pdfs.py` — gerador dos PDFs PT/EN/ES
