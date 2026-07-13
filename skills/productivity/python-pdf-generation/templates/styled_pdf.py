# -*- coding: utf-8 -*-
"""Styled PDF generator — copy and modify for your document."""
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Windows font paths (adjust for Linux/Mac)
FONT = "C:/Windows/Fonts/arial.ttf"
FONT_B = "C:/Windows/Fonts/arialbd.ttf"
FONT_I = "C:/Windows/Fonts/ariali.ttf"


class PDF(FPDF):
    def header(self):
        self.set_font("ui-ar", "B", 11)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(44, 62, 80)
        self.cell(0, 10, "  Document Title", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("ui-ar", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def stitle(self, t):
        """Section title with underline."""
        self.set_font("ui-ar", "B", 12)
        self.set_text_color(41, 128, 185)
        self.cell(0, 8, t, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(41, 128, 185)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def body(self, t):
        """Body paragraph."""
        self.set_font("ui-ar", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, t)
        self.ln(2)

    def bitem(self, bold, rest):
        """Bullet item with bold prefix."""
        self.set_font("ui-ar", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, f"  \u2022  {bold} {rest}")
        self.ln(1)

    def nitem(self, n, bold, rest):
        """Numbered item."""
        self.set_font("ui-ar", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, f"  {n}. {bold} {rest}")
        self.ln(1)


def generate(output_path):
    pdf = PDF()
    pdf.add_font("ui-ar", "", FONT)
    pdf.add_font("ui-ar", "B", FONT_B)
    pdf.add_font("ui-ar", "I", FONT_I)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- Content ---
    pdf.stitle("Section Title")
    pdf.body("Your paragraph text goes here. Supports Spanish: acentos, ñ, ¿, ¡")

    pdf.stitle("Numbered List")
    pdf.nitem(1, "First item:", "description of the first item.")
    pdf.nitem(2, "Second item:", "description of the second item.")
    pdf.ln(2)

    pdf.stitle("Table")
    col1, col2 = 50, 130
    pdf.set_font("ui-ar", "B", 9)
    pdf.set_fill_color(41, 128, 185)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(col1, 8, "  Header 1", border=1, fill=True)
    pdf.cell(col2, 8, "  Header 2", border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("ui-ar", "", 9)
    pdf.set_text_color(50, 50, 50)
    fill = False
    for label, value in [("Row 1", "Value 1"), ("Row 2", "Value 2")]:
        pdf.set_fill_color(235, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(col1, 8, f"  {label}", border=1, fill=True)
        pdf.cell(col2, 8, f"  {value}", border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        fill = not fill
    pdf.ln(4)

    pdf.stitle("Bullets")
    pdf.bitem("Key point:", "explanation of the key point.")
    pdf.bitem("Another point:", "explanation here.")

    # --- Output ---
    pdf.output(output_path)
    print(f"PDF created: {output_path}")


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "output.pdf"
    generate(out)
