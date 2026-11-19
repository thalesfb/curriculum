# ADR-0005: Dados do CV como JSON (Single Source of Truth)

## Status

Accepted

## Data

2026-03-28

## Contexto

O portfolio exibe dados profissionais (experiência, projetos, skills, educação) que também alimentam CVs em três idiomas. Precisamos de uma fonte única de dados para o site e os CVs, mantendo a apresentação visual existente dos PDFs.

## Decisão

Usar `data/cv.json` como **single source of truth** para todo conteúdo profissional.

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
2. **`generate_cvs.py`** — Script Python gera as variantes Markdown para ATS
3. **`scripts/generate_cv_pdfs.py`** — Preenche o DOCX aprovado com os dados localizados e exporta os três PDFs via Microsoft Word no Windows
4. **Figma i18n variables** — Textos do design espelham o JSON

### PDFs com layout fixo

O arquivo `refs/template/curriculo_thales_ferreira_pt.docx` é o modelo visual editável e `data/cv.json` é a fonte do conteúdo. O gerador modifica somente os textos nos parágrafos existentes e mantém estilos, fontes, espaçamento e estrutura do DOCX. O Microsoft Word exporta as variantes PT, EN e ES. A geração falha antes de atualizar `public/refs` se a paginação sair das três páginas ou um parágrafo de experiência se separar do primeiro bullet; não reduz fonte, margens ou espaçamento para acomodar conteúdo. A geração e a conferência visual são locais em Windows; a CI Linux não executa Word.

## Consequências

### Positivas

- Atualizar dados em um lugar atualiza site + CVs + Figma
- Validação de schema com Zod em build time
- Scripts Python geram variantes Markdown e os três PDFs visuais a partir da mesma fonte
- Formato JSON é versionável (git diff legível)

### Negativas

- JSON grande pode ficar difícil de editar manualmente
- Sem UI de edição (precisa editar JSON direto)

## Referências

- `data/cv.json` — Arquivo de dados
- `generate_cvs.py` — Script gerador de CVs
- `output/` — 12 CVs gerados
- `refs/template/curriculo_thales_ferreira_pt.docx` — modelo dos PDFs
- `scripts/generate_cv_pdfs.py` — gerador dos PDFs PT/EN/ES
