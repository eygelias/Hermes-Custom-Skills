---
name: python-pdf-generation
description: "Generate styled PDFs from scratch using Python (fpdf2). Headers, footers, tables, bullets, Unicode/Spanish text."
version: 1.0.0
author: hermes
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [PDF, Python, Documents, Generation, Productivity]
    related_skills: [nano-pdf]
---

# Python PDF Generation

Generate multi-page styled PDFs from scratch using **fpdf2** (pure Python, no system deps).

Use when: user asks for a document/report/handout as a PDF file, especially with Spanish text, tables, or structured sections.

For *editing* an existing PDF, use `nano-pdf` instead.

## Install

```bash
pip install fpdf2
```

On Hermes Windows, the system Python may be needed if the venv lacks pip:
```bash
/c/Users/ELY/AppData/Local/Programs/Python/Python314/python.exe script.py
```

## Core Pattern

See `templates/styled_pdf.py` — a working template with headers, footers, section titles, body text, bullet items, numbered items, and styled tables. For WhatsApp school poster-style infographics, copy `templates/whatsapp_school_5_column_infographic.py` and replace title, sections, bullets, icons, and student footer.

## Key Pitfalls

### 0. Windows/MSYS path verification

When running native Windows Python from Git Bash/MSYS, output paths can be surprising. Write PDFs using a Windows-style path (`C:/Users/ELY/Desktop/file.pdf`), then verify through the shell path:
```bash
/c/Users/ELY/AppData/Local/Programs/Python/Python314/python.exe script.py
ls -lh /c/Users/ELY/Desktop/file.pdf
```
If output appears at a literal `\\c\\Users\\...` / `\c\Users\...` path instead of the real Desktop, copy it to `/c/Users/ELY/Desktop/...`, remove the stray file, and only report success after `ls -lh /c/Users/ELY/Desktop/...` succeeds.

### 1. Unicode requires TTF fonts — core fonts are Latin-1 only

fpdf2's built-in core fonts (Helvetica, Courier, Times) only support Latin-1. Any em-dash (—), bullet (•), accented text (ó, ñ, ¿, ¡) **will crash** with `FPDFUnicodeEncodingException`.

**Fix:** Register a TTF font with `add_font()`:
```python
pdf.add_font("myfont", "", "/path/to/font.ttf")
pdf.add_font("myfont", "B", "/path/to/font-bold.ttf")
pdf.set_font("myfont", "", 10)
```

Windows fonts: `C:/Windows/Fonts/arial.ttf`, `arialbd.ttf` (bold), `ariali.ttf` (italic).

### 2. cell() + multi_cell() on the same line runs out of space

Using `cell()` for a label then `multi_cell()` for wrapping text on the same line causes `FPDFException: Not enough horizontal space to render a single character` because `multi_cell` starts from the current X position, which may be near the right margin after the cell.

**Fix:** Use `multi_cell()` for the entire line with manual prefix formatting:
```python
# BAD — breaks on long text
pdf.cell(30, 6, "Label:")
pdf.multi_cell(0, 6, "long text that wraps...")

# GOOD — single multi_cell with prefix
pdf.multi_cell(0, 6, "  Label: long text that wraps...")
```

### 3. fpdf2 API deprecations (v2.5+)

- `ln=True` → use `new_x=XPos.LMARGIN, new_y=YPos.NEXT` from `fpdf.enums`
- Core font names like "Arial" get silently substituted to "helvetica" with a deprecation warning. Always use `add_font()` with explicit TTF path.

### 4. Table rows with alternating colors

```python
fill = False
for row in data:
    pdf.set_fill_color(235, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
    pdf.cell(col_w, 8, "  text", border=1, fill=True,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    fill = not fill
```

### 5. System Python on Windows

Hermes venv may lack pip. Find the system Python:
```bash
ls /c/Users/ELY/AppData/Local/Programs/Python/Python*/python.exe
```
Then run scripts with that full path.

## Workflow

1. Clarify/use intended reading format before writing length: if the PDF content is meant to be copied by hand (exam sheets, notebook, classroom assignment), produce a compact 1-2 page version with short paragraphs and no heavy sections; avoid polished long reports unless requested.
2. Install fpdf2 (`pip install fpdf2`)
3. Copy `templates/styled_pdf.py` to the target location
4. Edit content sections (titles, body text, table rows, bullets)
5. Run with system Python if venv lacks fpdf2
6. Verify output file exists with `ls -lh`
7. Clean up the generator script

## User-facing document length pitfall

When user asks for a PDF of school/class content, do not assume "bien elaborado" means long. If they mention a classmate will copy it by hand, or it is for an exam sheet, prioritize handwriting-friendly brevity: title + 4-5 short sections, plain language, no cover page unless requested.

## WhatsApp school infographic PDFs for this user

- Create outputs under `C:/Users/ELY/Desktop/COSAS/` unless the user explicitly asks for another location; do not place new PDFs/scripts directly on the Desktop.
- If the user asks for another student using the same topic, make the PDF visibly different: change orientation, palette, layout structure, icons, and filename; do not only swap the name/ID.
- When the user says designs "se ven iguales" or asks for a different format, change the *structure*, not just colors: e.g. 5-column poster, magazine/cover layout, timeline, radial map, or split-page comparison.
- If user provides a reference image and says "más como está", emulate the broad layout features (numbered columns, dense bullets, internal drawings/icons, arrows, header/footer bands) without copying exact art or text.
- For school infographics, prefer more content + visible simple vector images/icons inside each section over sparse decorative cards. Draw icons with FPDF primitives when Pillow/images are unavailable.
- If emulating a reference infographic, copy only the broad structure (columns, density, image placement, arrows), not the exact text. Rewrite content for the requested topic/student.
- Before delivering a revised infographic after user visual corrections, render a PNG preview and inspect it for overlaps, cramped text, cut-off text, and decorative elements covering content.
- Avoid decorative elements that overlap text boxes (e.g. numbered circles intruding into cards); use top color bars, side strips, or clean labels instead.
- Put the student name and ID visibly at the bottom/footer when provided.
- If the user later asks for “1 sola página”, regenerate a one-page infographic (usually landscape) rather than trying to compress a multi-page PDF after the fact.
- For WhatsApp delivery, verify with `ls -lh` and return `MEDIA:C:/Users/ELY/Desktop/COSAS/<file>.pdf`.

## Notebook-copy school research PDFs

For school research that must be copied into a notebook:

1. Keep each topic compact: short paragraph + 4-6 bullets maximum.
2. Add a final "resumen para copiar rápido" page when there are many topics.
3. If the user requests images but also says they must be easy to replicate/draw, prefer simple vector drawings made with FPDF primitives (`line`, `rect`, `ellipse`, arrows, labels) instead of external image files. Examples: waves, staff lines + notes, arrows, letter blocks (A-B-A), simple instrument icons.
4. Under each representative drawing, add a short "Dibujo fácil:" instruction so the student knows what to copy.
5. Do not let decorative polish make the PDF longer; drawings should clarify and be quick to redraw.

### FPDF layout pitfall: centered `multi_cell`

On fpdf2, centered cover text can fail with `FPDFException: Not enough horizontal space to render a single character` if `multi_cell(0, ...)` is called from a bad X position or without explicit cursor movement. Safer pattern:

```python
from fpdf.enums import XPos, YPos
pdf.multi_cell(180, 9, "Title", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
```

Use explicit width near page content width and `new_x/new_y` for cover/title blocks.
