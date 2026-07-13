# Bitácora de práctica profesional — fixed Word form example

## User correction captured

When preparing a bitácora that will be copied by hand into a printed form, do **not** enlarge boxes, change table dimensions, alter margins, or redesign layout. The text must be shortened to fit the existing boxes, especially if the user writes large.

Guide notes inside form headers are references only and can be removed from the filled version:

- `(Lo que escucho y veo)` → content for `Descriptiva` box.
- `(Vinculación con la Normativa Legal)` → content for `Dimensión Normativa y Técnica` box.
- `(¿Qué me llamó la atención? ¿Cómo me sentí?)` → content for `Dimensión Reflexiva` box.

## Pattern that worked

1. Use original Word file as template.
2. Duplicate original form page for each day.
3. Fill concise text only.
4. Preserve original geometry.
5. Remove guide parentheticals.
6. Verify by opening the output with Microsoft Word.

## Corruption symptom

Word error seen after naive XML cloning:

> El archivo ... no se puede abrir porque hay problemas con el contenido.  
> Ubicación: Parte: `/word/document.xml`, Línea: 2, Columna: 0

Likely cause: duplicated drawing properties IDs in cloned logos/images (`wp:docPr/@id`).

## Repair approach

If cloned DOCX pages include images/logos, inspect and renumber all `wp:docPr` IDs uniquely inside `word/document.xml`:

```python
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree

src = Path('input.docx')
out = Path('output_fixed.docx')
ns = {'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}

with ZipFile(src, 'r') as zin, ZipFile(out, 'w', ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == 'word/document.xml':
            root = etree.fromstring(data)
            for i, el in enumerate(root.xpath('.//wp:docPr', namespaces=ns), start=1):
                el.set('id', str(i))
            data = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        zout.writestr(item, data)
```

Then verify with Microsoft Word COM if available:

```python
import win32com.client as win32
word = win32.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(r'C:\path\output_fixed.docx', ReadOnly=True, AddToRecentFiles=False, OpenAndRepair=False)
    print('WORD_OPEN_OK', 'tables=', doc.Tables.Count, 'pages=', doc.ComputeStatistics(2))
    doc.Close(False)
finally:
    word.Quit()
```

## Text style for this class of document

- Spanish formal, simple.
- Not too extensive.
- One compact paragraph per box.
- Observation role: emphasize `observé`, `escuché`, `vi`, `aprendí`, not teaching action if user was only observer.
- Closing day with no children/classes can still be logged as institutional closure, gratitude, sharing with teachers, and delivery of supplies.