# ADR-0005: Dados do CV como JSON (Single Source of Truth)

## Status

Accepted

## Data

2026-03-28

## Contexto

O portfolio exibe dados profissionais (experiência, projetos, skills, educação) que também são usados para gerar CVs otimizados para ATS em 12 variantes (4 cargos × 3 idiomas). Precisamos de uma fonte única de dados que alimente tanto o site quanto os CVs.

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
2. **`generate_cvs.py`** — Script Python gera 12 markdowns ATS-otimizados
3. **Figma i18n variables** — Textos do design espelham o JSON

## Consequências

### Positivas

- Atualizar dados em um lugar atualiza site + CVs + Figma
- Validação de schema com Zod em build time
- Script Python existente já gera 12 CVs automaticamente
- Formato JSON é versionável (git diff legível)

### Negativas

- JSON grande pode ficar difícil de editar manualmente
- Sem UI de edição (precisa editar JSON direto)

## Referências

- `data/cv.json` — Arquivo de dados
- `generate_cvs.py` — Script gerador de CVs
- `output/` — 12 CVs gerados
