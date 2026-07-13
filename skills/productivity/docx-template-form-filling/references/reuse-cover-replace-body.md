# Reuse a DOCX cover while replacing the body

Use when user supplies a finished Word document as visual template and asks for a new paper that keeps its cover, logos, letterhead, margins, and theme.

## Safe approach

1. Open original with `python-docx`; do not rebuild cover.
2. Inspect paragraphs, sections, floating drawings, tables, and page settings.
3. Locate exact cover/body boundary by paragraph index and visible text.
4. Edit only cover text fields that must change (title, names, IDs, date).
5. Preserve paragraphs containing `wp:anchor` drawings. Floating logos may not appear in `inline_shapes`.
6. Remove old body elements after boundary, then append new body before `sectPr`.
7. Set `page_break_before=True` on first body heading so new content starts after cover without inserting an accidental blank page.

## Minimal body replacement

```python
from docx import Document

doc = Document(source)

# Example: cover occupies paragraphs 0..25.
for paragraph in list(doc.paragraphs[26:]):
    paragraph._element.getparent().remove(paragraph._element)

intro = doc.add_paragraph("Introducción")
intro.paragraph_format.page_break_before = True
# Append remaining headings and body paragraphs.
doc.save(output)
```

When replacing text inside an existing cover paragraph, clear runs only in that paragraph. Never recreate paragraphs holding floating drawings unless drawings are intentionally removed.

## Verification

Reopen output with `python-docx` and verify:

- page width, height, margins, and section count match template;
- expected cover text and every requested section appear exactly once;
- old title, old student names, and old body text are absent;
- expected number of `wp:anchor` drawings and image relationships remains;
- first body heading has `page_break_before=True`;
- output ZIP passes `ZipFile.testzip()` and contains `word/document.xml` plus expected `word/media/*` files.

Example anchor count:

```python
from docx.oxml.ns import qn
anchors = sum(
    1
    for p in doc.paragraphs
    for _ in p._p.iter(qn("wp:anchor"))
)
```

## Common pitfalls

- `len(doc.inline_shapes) == 0` does not mean document has no images; logos may be floating `wp:anchor` objects.
- Replacing whole document from scratch loses anchor positioning, theme data, and cover geometry.
- Adding a manual page-break paragraph after a cover that already fills one page can create a blank page. Prefer `page_break_before` on first body heading.
- Longer student names or identity numbers may wrap in narrow indented cover columns. Preserve indentation, then slightly reduce only those runs' font size if needed.
