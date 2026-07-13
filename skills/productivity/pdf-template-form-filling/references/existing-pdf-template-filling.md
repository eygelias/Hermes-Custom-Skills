# Existing PDF template filling without altering format

Use when the user provides a PDF template and source content, and explicitly says not to alter dimensions/format.

## Principle

Do **not** recreate the table/layout from scratch unless the user asks for a redesigned document. Keep the original PDF page, logos, borders, headers, and dimensions. Only remove and replace text inside existing fields.

## PyMuPDF workflow

1. Inspect template geometry:

```python
import fitz
pdf = fitz.open("template.pdf")
page = pdf[0]
print(page.rect)
for b in page.get_text("blocks"):
    x0, y0, x1, y1, text, *_ = b
    print((round(x0,1), round(y0,1), round(x1,1), round(y1,1)), repr(text[:120]))
```

2. Render original preview before editing:

```python
page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save("preview_original_p1.png")
```

3. Redact only text content areas, not headers/labels/borders:

```python
page.add_redact_annot(fitz.Rect(153, 190, 806, 226), fill=(1,1,1))
page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
```

4. Register fonts after redaction and insert replacement text:

```python
page.insert_font(fontname="Arial", fontfile="C:/Windows/Fonts/arial.ttf")
page.insert_textbox(
    fitz.Rect(154, 194, 806, 226),
    replacement_text,
    fontsize=8.2,
    fontname="Arial",
    lineheight=1.05,
)
```

5. If redaction hides table borders, redraw only the original affected lines:

```python
black = (0, 0, 0)
page.draw_line((16, 234), (806, 234), color=black, width=0.6, overlay=True)
page.draw_line((391, 234), (391, 516), color=black, width=0.6, overlay=True)
```

6. Render output preview and compare visually before delivery.

## Bitácora/form-table pitfall

For bitácora-style forms, do not merge separate cells. Preserve semantics:

- left columns: `Descriptiva`, `Dimensión Normativa y Técnica`, `Dimensión Reflexiva`
- right column: `Descripción general de las actividades...`
- activity field remains in its original row

If the user says “alteraste el formato”, restart from the original template and patch only text rectangles.
