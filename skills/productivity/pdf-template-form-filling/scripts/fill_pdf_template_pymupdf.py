"""PyMuPDF helper skeleton for filling an existing PDF template without changing page size.

Copy this script, set SOURCE_PDF / TEMPLATE_PDF / OUTPUT_PDF, then customize
`entries` and `draw_page()` for the target template.
"""
from pathlib import Path
import fitz

TEMPLATE_PDF = r"C:/path/to/template.pdf"
SOURCE_PDF = r"C:/path/to/source.pdf"
OUTPUT_PDF = r"C:/Users/ELY/Desktop/COSAS/filled_template.pdf"
FONT = r"C:/Windows/Fonts/arial.ttf"
FONT_B = r"C:/Windows/Fonts/arialbd.ttf"


def extract_preview(path: str, chars: int = 2000) -> None:
    doc = fitz.open(path)
    print(path, "pages=", doc.page_count, "size=", tuple(doc[0].rect))
    print(doc[0].get_text("text")[:chars])


def put(page, rect, text, size=8, bold=False, align=0):
    font = "ArialB" if bold else "Arial"
    return page.insert_textbox(
        rect,
        text,
        fontsize=size,
        fontname=font,
        color=(0, 0, 0),
        align=align,
        lineheight=1.05,
    )


def draw_page(page, entry):
    page.insert_font(fontname="Arial", fontfile=FONT)
    page.insert_font(fontname="ArialB", fontfile=FONT_B)

    # Example: preserve header, clean writable body region only.
    page.draw_rect(fitz.Rect(10, 128, 832, 548), color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

    # TODO: redraw table borders/labels to match template.
    page.draw_rect(fitz.Rect(16, 134, 826, 522), color=(0, 0, 0), width=0.7)

    # TODO: fill exact fields.
    put(page, fitz.Rect(30, 150, 810, 190), entry["title"], size=9, bold=True)
    put(page, fitz.Rect(30, 200, 810, 500), entry["body"], size=8)


def main():
    extract_preview(SOURCE_PDF)
    extract_preview(TEMPLATE_PDF)

    entries = [
        {"title": "Actividad", "body": "Texto resumido para encajar en el formato."},
    ]

    doc = fitz.open(TEMPLATE_PDF)
    for i, entry in enumerate(entries[: doc.page_count]):
        draw_page(doc[i], entry)

    Path(OUTPUT_PDF).parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT_PDF, garbage=4, deflate=True)
    doc.close()

    # Verify size/page count and render page 1 preview.
    orig = fitz.open(TEMPLATE_PDF)
    out = fitz.open(OUTPUT_PDF)
    assert orig.page_count == out.page_count
    assert tuple(orig[0].rect) == tuple(out[0].rect)
    out[0].get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(str(Path(OUTPUT_PDF).with_suffix(".preview_p1.png")))
    print(OUTPUT_PDF)


if __name__ == "__main__":
    main()
