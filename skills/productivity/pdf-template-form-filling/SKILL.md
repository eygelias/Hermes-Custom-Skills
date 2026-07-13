---
name: pdf-template-form-filling
description: Fill existing PDF forms/templates from source notes while preserving original page size and visual format.
version: 1.0.0
author: hermes
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [PDF, Documents, Forms, Templates, PyMuPDF, Productivity]
    related_skills: [ocr-and-documents, nano-pdf, python-pdf-generation]
---

# PDF Template Form Filling

Use when the user provides:

- a blank or partially-filled PDF format/template,
- a source PDF/document with observations or notes,
- and asks to fill the template **without altering dimensions or format**.

Goal: preserve original PDF page size and overall layout, while replacing/adding readable content into the existing fields.

## Preferred Tooling

Reusable starter script: `scripts/fill_pdf_template_pymupdf.py`.

Use **PyMuPDF (`fitz`)**. It can:

- read PDF text,
- preserve original page boxes,
- draw white rectangles to clean old text,
- redraw simple table lines,
- insert text into exact boxes,
- render preview images for visual verification.

Install if needed:

```bash
python3 -m pip install pymupdf
```

## Workflow

For coordinate-based PyMuPDF filling and the “preserve exact visual format” correction, see `references/existing-pdf-template-filling.md`. Use that pattern when the user complains that a filled form altered the original layout.

1. **Extract both documents first**
   ```python
   import fitz
   for path in [source_pdf, template_pdf]:
       doc = fitz.open(path)
       print(path, doc.page_count, doc[0].rect)
       print(doc[0].get_text("text")[:2000])
   ```

2. **Identify the template structure**
   - Page count.
   - Page dimensions.
   - Header area to preserve.
   - Form/table area to fill.
   - Existing sample text or placeholders.

3. **Preserve page size**
   - Open template PDF and edit its pages directly.
   - Do not recreate a new PDF from scratch unless user asked for redesign.
   - Save to a new output path under the user’s requested folder.

4. **Avoid text-over-text**
   - If the template already contains old/sample content, do not just insert new text over it.
   - Cover only writable regions with white rectangles.
   - Redraw needed borders/labels.
   - Then insert new content.

5. **Use real fonts for Spanish**
   ```python
   page.insert_font(fontname="Arial", fontfile="C:/Windows/Fonts/arial.ttf")
   page.insert_font(fontname="ArialB", fontfile="C:/Windows/Fonts/arialbd.ttf")
   page.insert_textbox(rect, text, fontsize=8, fontname="Arial")
   ```

6. **Keep text concise enough to fit**
   - Existing PDF cells are limited.
   - Summarize source notes into clear paragraphs.
   - Reduce font size only as needed.
   - Never allow text to bleed outside the cell.

7. **Verify dimensions and page count**
   ```python
   orig = fitz.open(template_pdf)
   out = fitz.open(output_pdf)
   assert orig.page_count == out.page_count
   assert tuple(orig[0].rect) == tuple(out[0].rect)
   ```

8. **Render and inspect preview before delivery**
   ```python
   p = out[0]
   p.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save("preview_p1.png")
   ```
   Use vision on preview. Check:
   - no overlapping text,
   - fields aligned,
   - format still resembles original,
   - content readable.

9. **Clean temporary scripts/previews**
   Leave only final output unless user wants working files.

## Layout Strategy: Clean Region + Redraw Table

Best when existing template is already filled or OCR text sits in the way:

```python
import fitz

doc = fitz.open(template_pdf)
page = doc[0]

# preserve header, clean only form body
page.draw_rect(fitz.Rect(10, 128, 832, 548), color=(1,1,1), fill=(1,1,1), overlay=True)

# redraw table lines/labels
page.draw_rect(fitz.Rect(16, 134, 826, 205), color=(0,0,0), width=0.7)
page.draw_line((16,154), (826,154), color=(0,0,0), width=0.7)

# insert new text
page.insert_font(fontname="Arial", fontfile="C:/Windows/Fonts/arial.ttf")
page.insert_textbox(fitz.Rect(156, 220, 818, 247), actividad, fontsize=8, fontname="Arial")

doc.save(output_pdf, garbage=4, deflate=True)
```

## Common Pitfalls

- **Extracted text is not visual proof.** A PDF can extract correctly while the page visually has text overlap. Always render preview.
- **Blind overlay fails on already-filled templates.** Clean old content first.
- **Too much text breaks format.** Summarize into field-sized paragraphs.
- **Recreating from scratch can violate “sin alterar formato”.** Edit template copy instead.
- **“Same dimensions” is not enough.** The user may mean exact visual format: original lines, labels, logos, cell semantics, and spacing. Preserve those too.
- **Do not merge table cells semantically.** If the form has separate areas (for example Descriptiva / Normativa / Reflexiva plus a right-side general description), write each kind of content into its matching original cell.
- **Core fonts can fail with Spanish/Unicode.** Use TTF fonts.

## User-Facing Delivery Pattern

After verification:

```text
Listo. Llené el formato sin cambiar dimensión del PDF y corregí texto sobrepuesto.

MEDIA:C:/Users/ELY/Desktop/COSAS/<archivo_final>.pdf
```
