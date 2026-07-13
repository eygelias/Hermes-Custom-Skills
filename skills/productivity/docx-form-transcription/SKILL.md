---
name: docx-form-transcription
description: Fill or prepare Word .docx forms for handwritten transcription while preserving the original printed layout exactly.
---

# DOCX Form Transcription

Use when user provides a Word form/template or screenshot of a printed form and asks for text to copy by hand, especially bitácoras, school forms, logs, internship records, or institutional templates.

## Core rule

Preserve form geometry. Do **not** redesign table, page, margins, orientation, row heights, column widths, logos, borders, headers, or cell dimensions unless user explicitly asks. The deliverable is text adapted to fit the existing printed boxes.

## Workflow

1. Start from the original `.docx` template when available.
2. Inspect table structure before editing:
   - number of tables
   - rows/columns
   - merged-cell layout
   - section/page settings
3. Fill only text content.
4. Keep text short enough for user handwriting. If user says their handwriting is large:
   - summarize aggressively
   - prefer 1 short paragraph per box
   - avoid long sentences
   - avoid repeating facts across boxes
5. Treat parenthetical prompts as guidance, not content. Example prompts to remove from filled output:
   - `(Lo que escucho y veo)`
   - `(Vinculación con la Normativa Legal)`
   - `(¿Qué me llamó la atención? ¿Cómo me sentí?)`
6. Keep only field labels/titles that belong to the form, e.g. `Descriptiva`, `Dimensión Normativa y Técnica`, `Dimensión Reflexiva`.
7. If multiple days/pages are needed, duplicate the original page/template without changing its geometry.
8. Verify the result opens in Microsoft Word, not only `python-docx`.

## DOCX safety pitfalls

- Naively deep-copying Word XML pages that contain images/logos can corrupt the file because drawing IDs (`wp:docPr/@id`) may be duplicated. Word may report: `El archivo ... no se puede abrir porque hay problemas con el contenido` at `/word/document.xml`.
- After cloning pages with images, renumber all `wp:docPr` IDs uniquely or use Microsoft Word COM automation to insert pages/templates.
- `python-docx` can read/write many forms, but Microsoft Word is final verifier for `.docx` validity.
- Merged tables may behave differently in Word COM: accessing `Rows(n).Cells` can fail when table has vertical merges. If that happens, edit via `python-docx` after generating a valid repeated template.

## Verification checklist

- Original and output have same page size, orientation, and margins.
- Each repeated form has same table shape and merged-cell pattern.
- User guide prompts are removed if requested.
- Text fits the box for handwriting.
- Microsoft Word opens the output without repair/content warnings.

## References

- See `references/bitacora-practica-profesional.md` for a worked example: preserving a UPEL bitácora format, shortening daily observations, and repairing duplicated `wp:docPr` IDs.