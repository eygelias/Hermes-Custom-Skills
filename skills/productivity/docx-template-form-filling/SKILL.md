---
name: docx-template-form-filling
description: "Fill existing Word/DOCX form templates without changing layout; preserve table geometry, margins, orientation, and cell dimensions while adapting text for print or handwritten transcription."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [docx, word, forms, templates, python-docx, handwriting]
    related_skills: [ocr-and-documents]
---

# DOCX Template Form Filling

Use when user provides a Word form/template and asks to fill, transcribe, summarize into boxes, preserve format, or create a printable/handwritten version.

Core rule: **never rebuild template from scratch unless user asks.** Open original `.docx`, clone its structure if multiple pages needed, then replace text only.

## Workflow

1. **Inspect template before writing**
   - Load with `python-docx`.
   - Count sections, tables, rows/columns, merged-cell patterns.
   - Record page size, margins, orientation.
   - Identify which cells are labels and which cells are writable areas.

2. **Preserve layout exactly**
   - Do not change margins, orientation, page size, table widths, row heights, column widths, borders, or merge structure.
   - Do not create a new approximate table if an original template exists.
   - For repeated daily forms, clone the original document body/table for each day, preserving section properties.

3. **Reuse finished-document covers safely**
   - When user wants a new paper based on an existing document, preserve the original cover instead of rebuilding it.
   - Inspect both `inline_shapes` and floating `wp:anchor` drawings; a DOCX can report zero inline shapes while still containing logos and other floating images.
   - Identify the cover/body paragraph boundary, edit only required cover fields, remove old body elements after that boundary, then append new content.
   - Preserve paragraphs containing anchored drawings. Start the new body with `page_break_before=True` rather than inserting a separate break that may create a blank page.
   - Follow `references/reuse-cover-replace-body.md` for code and structural verification.

4. **Adapt text to available boxes**
   - If user will handwrite and says their handwriting is large: write shorter text, not smaller boxes.
   - Prefer concise, complete sentences that fit the visible box.
   - Put detailed narrative only in the largest description box.
   - Dimension/reflection boxes get 1–3 short sentences max unless space clearly allows more.

5. **Handle guide notes/placeholders**
   - Parenthetical instructions like `(Lo que escucho y veo)`, `(Vinculación con la Normativa Legal)`, `(¿Qué me llamó la atención? ¿Cómo me sentí?)` are reference prompts, not final content.
   - Remove guide notes from final filled form unless user explicitly wants them kept.
   - Keep clean headers such as `Descriptiva`, `Dimensión Normativa y Técnica`, `Dimensión Reflexiva`.

6. **Verify before final**
   - Reopen output `.docx`.
   - Confirm same section page settings as template.
   - Confirm each filled table has same row/column count and merged-cell pattern as template.
   - For cover reuse, confirm floating-anchor count, image relationships, expected cover fields, absence of old body text, and package ZIP integrity.
   - Search output text to ensure guide notes were removed when requested.
   - Report path and exactly what was preserved.

## Python pattern

```python
from copy import deepcopy
from docx import Document
from docx.enum.text import WD_BREAK
from docx.oxml.ns import qn

TEMPLATE = "template.docx"
OUT = "filled.docx"

def unique_cells(row):
    seen, out = set(), []
    for cell in row.cells:
        key = id(cell._tc)
        if key not in seen:
            seen.add(key)
            out.append(cell)
    return out

def clone_template_pages(doc, copies):
    body = doc.element.body
    sectPr = body.sectPr
    elems = [deepcopy(el) for el in list(body) if el.tag != qn('w:sectPr')]
    for _ in range(copies - 1):
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        if sectPr is not None and sectPr.getparent() is not None:
            body.remove(sectPr)
        for el in elems:
            body.append(deepcopy(el))
        if sectPr is not None:
            body.append(sectPr)

doc = Document(TEMPLATE)
clone_template_pages(doc, copies=5)
doc.save(OUT)
```

Use `unique_cells(row)` when addressing merged cells: `python-docx` exposes repeated cell references for merged regions.

## Pitfalls

- Recreating a DOCX table visually similar to a screenshot changes dimensions; bad for forms that must be copied by hand.
- Large fonts do not solve handwritten transcription; shorter text solves it.
- Do not leave instructional prompt text inside answer boxes unless user asks.
- If dependency is missing, install or use available Python environment, but do not encode transient install failures as durable rules.

## References

- `references/handwritten-bitacora.md` — Spanish educational bitácora example: filling daily practice logs for handwriting while preserving original format.
