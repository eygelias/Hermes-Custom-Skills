"""Template: WhatsApp school infographic PDF, 5-column poster style.

Copy and modify for user-requested school infographics that should look like a
reference poster: dense numbered columns, internal vector icons, arrows,
header/footer bands, student name at bottom.

Output path should stay under C:/Users/ELY/Desktop/COSAS/ for this user.
"""
from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUT = 'C:/Users/ELY/Desktop/COSAS/infografia_5_columnas.pdf'
FONT = 'C:/Windows/Fonts/arial.ttf'
FONT_B = 'C:/Windows/Fonts/arialbd.ttf'
STUDENT = 'Nombre Apellido  V-00000000'
TITLE = 'TÍTULO DE LA INFOGRAFÍA'
SUBTITLE = 'Subtítulo o contexto'

SECTIONS = [
    ('1. SECCIÓN UNO', 'Subtítulo', ['Punto importante', 'Segundo punto', 'Tercer punto'], (12, 140, 190), 'warning'),
    ('2. SECCIÓN DOS', 'Subtítulo', ['Punto importante', 'Segundo punto', 'Tercer punto'], (20, 155, 105), 'school'),
    ('3. SECCIÓN TRES', 'Subtítulo', ['Punto importante', 'Segundo punto', 'Tercer punto'], (235, 135, 45), 'community'),
    ('4. SECCIÓN CUATRO', 'Subtítulo', ['Punto importante', 'Segundo punto', 'Tercer punto'], (112, 65, 150), 'global'),
    ('5. SECCIÓN CINCO', 'Subtítulo', ['Punto importante', 'Segundo punto', 'Tercer punto'], (220, 55, 95), 'teacher'),
]

class PDF(FPDF):
    def add_fonts(self):
        self.add_font('ArialTTF','',FONT)
        self.add_font('ArialTTF','B',FONT_B)

    def bullet_text(self, x, y, w, items, color):
        self.set_font('ArialTTF','B',8.2)
        cy = y
        for item in items:
            self.set_fill_color(*color)
            self.ellipse(x, cy+1, 2.2, 2.2, 'F')
            self.set_text_color(30,30,35)
            self.set_xy(x+4, cy)
            self.multi_cell(w-4, 3.9, item, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            cy = self.get_y() + 1.2

    def simple_icon(self, name, cx, cy, color):
        self.set_draw_color(35,35,35)
        self.set_fill_color(*color)
        if name == 'school':
            self.rect(cx-16, cy-3, 32, 24, 'DF')
            self.polygon([(cx-19,cy-3),(cx,cy-20),(cx+19,cy-3)], style='F')
        elif name == 'community':
            self.ellipse(cx-18, cy-18, 36, 26, 'F')
            self.set_draw_color(100,70,40); self.line(cx, cy+8, cx, cy+28)
            for dx in (-16,0,16): self.ellipse(cx+dx-4, cy+34, 8, 8, 'DF')
        elif name == 'global':
            self.ellipse(cx-16, cy-16, 32, 32, 'DF')
            self.rect(cx+18, cy-15, 22, 13, 'DF')
            self.rect(cx+18, cy+6, 22, 13, 'DF')
        elif name == 'teacher':
            self.ellipse(cx-9, cy-18, 18, 18, 'DF')
            self.polygon([(cx-18,cy+4),(cx+18,cy+4),(cx+24,cy+42),(cx-24,cy+42)], style='F')
        else:
            self.polygon([(cx,cy-22),(cx+18,cy+18),(cx-18,cy+18)], style='DF')
            self.set_text_color(255,255,255); self.set_font('ArialTTF','B',16); self.text(cx-3, cy+11, '!')

    def draw_card(self, x, y, w, h, color, title, subtitle, bullets, icon):
        light = tuple(min(255, int(c + (255-c)*0.75)) for c in color)
        self.set_fill_color(*light); self.rect(x, y, w, h, 'F')
        self.set_draw_color(*color); self.set_line_width(1); self.rect(x, y, w, h)
        self.set_fill_color(*color); self.rect(x, y, w, 17, 'F')
        self.set_text_color(255,255,255); self.set_font('ArialTTF','B',9.8)
        self.set_xy(x+2, y+2); self.multi_cell(w-4,4.5,title,align='C',new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        self.set_text_color(10,10,10); self.set_font('ArialTTF','B',9.7)
        self.set_xy(x+4,y+22); self.multi_cell(w-8,4.8,subtitle,align='C',new_x=XPos.LMARGIN,new_y=YPos.NEXT)
        self.simple_icon(icon, x+w/2, y+50, color)
        self.bullet_text(x+5, y+76, w-9, bullets, color)

pdf = PDF('L','mm','A4')
pdf.set_auto_page_break(False)
pdf.add_fonts()
pdf.add_page()
pdf.set_fill_color(231,248,252); pdf.rect(0,0,297,210,'F')
pdf.set_fill_color(0,86,140); pdf.rect(0,0,297,28,'F')
pdf.set_fill_color(255,210,70); pdf.rect(0,28,297,4,'F')
pdf.set_text_color(255,255,255); pdf.set_font('ArialTTF','B',18)
pdf.set_xy(12,5); pdf.multi_cell(273,7,TITLE,align='C',new_x=XPos.LMARGIN,new_y=YPos.NEXT)
pdf.set_font('ArialTTF','',8.5); pdf.set_xy(12,22); pdf.cell(273,4,SUBTITLE,align='C')

xs = [10, 68, 126, 184, 242]
ws = [52, 52, 52, 52, 45]
for x, w, section in zip(xs, ws, SECTIONS):
    pdf.draw_card(x, 40, w, 145, section[3], section[0], section[1], section[2], section[4])

for x, c in zip([62,120,178,236], [s[3] for s in SECTIONS[:-1]]):
    pdf.set_fill_color(*c)
    pdf.polygon([(x+1,100),(x+9,100),(x+9,95),(x+20,106),(x+9,117),(x+9,112),(x+1,112)], style='F')

pdf.set_fill_color(0,86,140); pdf.rect(0,190,297,20,'F')
pdf.set_text_color(255,255,255); pdf.set_font('ArialTTF','B',11)
pdf.set_xy(10,194); pdf.cell(277,5,STUDENT, align='R')
pdf.output(OUT)
print(OUT)
