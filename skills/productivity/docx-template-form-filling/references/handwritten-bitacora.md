# Handwritten Spanish bitácora forms

Session-derived pattern for Venezuelan educational practice logs (`BITÁCORA PARA EL REGISTRO DE LA PRÁCTICA PROFESIONAL`).

## User-facing requirement pattern

User may provide:
- screenshot/photo of form,
- original `.docx` template,
- daily rough notes,
- request: "lo debo transcribir a mano", "mi letra es grande", "mantén el formato igual".

Interpretation:
- Output should be a DOCX aid for copying by hand, not a dense typed final report.
- Preserve original form geometry exactly.
- Text must be short enough for large handwriting inside printed boxes.

## Content mapping

Typical boxes:

- **Actividad**: one concise line naming the day activity.
- **Descriptiva**: what was seen/heard; classroom observations only.
- **Dimensión Normativa y Técnica**: connection to classroom norms, inclusion, participation, routine, pedagogy, legal/educational principles; keep general unless exact law required.
- **Dimensión Reflexiva**: what stood out and how practitioner felt as observer/future teacher.
- **Descripción general**: concise full narrative of day; largest box gets most detail.

Guide notes often printed in template:
- `(Lo que escucho y veo)`
- `(Vinculación con la Normativa Legal)`
- `(¿Qué me llamó la atención? ¿Cómo me sentí...)`

These are prompts, not answer text. Remove them from filled version if user asks or if they clutter handwritten-copy output.

## Style for Carlos/Ely

Spanish. Direct. No long explanation. Produce the file on Desktop when requested.

For large handwriting:
- description boxes: ~45–75 words each,
- dimension boxes: ~20–35 words each,
- activity: 1 line,
- avoid paragraphs that fill every inch of the form.

## Verification checklist

After generating DOCX from template:

```python
from docx import Document

def merged_pattern(table):
    return [(len(row.cells), len({id(c._tc) for c in row.cells})) for row in table.rows]

base = Document('BITÁCORA.docx')
out = Document('filled.docx')
assert len(out.tables) == expected_days
assert all((len(t.rows), len(t.columns)) == (len(base.tables[0].rows), len(base.tables[0].columns)) for t in out.tables)
assert merged_pattern(out.tables[0]) == merged_pattern(base.tables[0])

text = '\n'.join(c.text for t in out.tables for r in t.rows for c in r.cells)
for phrase in ['Lo que escucho y veo', 'Vinculación con la Normativa Legal', 'Qué me llamó la atención']:
    assert phrase not in text
```

Also compare section settings: page size, margins, orientation.
