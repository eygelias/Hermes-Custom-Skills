# LibreOffice Spanish Venezuela DOCX fix

Session learning: LibreOffice can underline nearly every Spanish word in red even when Spanish dictionaries are installed. In a tested case, the DOCX carried English style metadata:

```xml
<w:lang w:val="en"/>
```

Changing LibreOffice UI/default language alone may not fix that existing document. Patch both the LibreOffice profile default locale and the DOCX language tags.

## Tested paths

```text
C:\Users\ELY\AppData\Roaming\LibreOffice\4\user\registrymodifications.xcu
C:\Program Files\LibreOffice\share\extensions\dict-es\es_VE.dic
C:\Program Files\LibreOffice\share\extensions\dict-es\es_VE.aff
```

## Tested script

Adapt `<DOCX>` before running. Always close LibreOffice first.

```python
from pathlib import Path
import zipfile, shutil, re

CONFIG = Path(r'C:/Users/ELY/AppData/Roaming/LibreOffice/4/user/registrymodifications.xcu')
DOCX = Path(r'<DOCX>')

if not CONFIG.exists():
    raise SystemExit(f'No existe configuración: {CONFIG}')
backup_config = CONFIG.with_suffix(CONFIG.suffix + '.bak-es-ve')
if not backup_config.exists():
    shutil.copy2(CONFIG, backup_config)

text = CONFIG.read_text(encoding='utf-8')
old = '<item oor:path="/org.openoffice.Office.Linguistic/General"><prop oor:name="DefaultLocale" oor:op="fuse"><value></value></prop></item>'
new = '<item oor:path="/org.openoffice.Office.Linguistic/General"><prop oor:name="DefaultLocale" oor:op="fuse"><value>es-VE</value></prop></item>'
if old in text:
    text = text.replace(old, new, 1)
elif 'oor:name="DefaultLocale"' in text:
    text = re.sub(r'(<item oor:path="/org\.openoffice\.Office\.Linguistic/General"><prop oor:name="DefaultLocale"[^>]*><value>)(.*?)(</value></prop></item>)', r'\1es-VE\3', text, count=1)
else:
    text = text.replace('</oor:items>', new + '\n</oor:items>')

text = re.sub(
    r'(<item oor:path="/org\.openoffice\.Office\.Linguistic/General/DictionaryList"><prop oor:name="ActiveDictionaries"[^>]*><value>)(.*?)(</value></prop></item>)',
    r'\1<it>Lista de palabras ignoradas</it><it>Español Venezuela.dic</it>\3',
    text,
    count=1,
)
CONFIG.write_text(text, encoding='utf-8')

if DOCX.exists():
    backup_docx = DOCX.with_suffix(DOCX.suffix + '.bak-es-ve')
    if not backup_docx.exists():
        shutil.copy2(DOCX, backup_docx)
    tmp = DOCX.with_suffix('.tmp.docx')
    changed = []
    with zipfile.ZipFile(DOCX, 'r') as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith('word/') and item.filename.endswith('.xml'):
                s = data.decode('utf-8', 'ignore')
                before = s
                s = re.sub(r'<w:lang\b[^>]*/>', '<w:lang w:val="es-VE" w:eastAsia="es-VE" w:bidi="es-VE"/>', s)
                s = re.sub(r'w:val="(?:en|en-US|es|es-ES|es-MX)"', 'w:val="es-VE"', s)
                if s != before:
                    data = s.encode('utf-8')
                    changed.append(item.filename)
            zout.writestr(item, data)
    tmp.replace(DOCX)
    print('DOCX actualizado:', DOCX)
    print('XML modificados:', ', '.join(changed) if changed else 'ninguno')
    print('Backup DOCX:', backup_docx)

print('LibreOffice configurado: DefaultLocale=es-VE')
print('Backup config:', backup_config)
```

## Verification

```python
from pathlib import Path
import zipfile, re
cfg = Path(r'C:/Users/ELY/AppData/Roaming/LibreOffice/4/user/registrymodifications.xcu')
print('DefaultLocale es-VE:', '<value>es-VE</value>' in cfg.read_text(encoding='utf-8'))
for p in [Path(r'C:/Program Files/LibreOffice/share/extensions/dict-es/es_VE.dic'), Path(r'C:/Program Files/LibreOffice/share/extensions/dict-es/es_VE.aff')]:
    print('dict exists:', p.exists(), p)
with zipfile.ZipFile(Path(r'<DOCX>')) as z:
    styles = z.read('word/styles.xml').decode('utf-8', 'ignore')
    print('doc styles es-VE:', 'w:val="es-VE"' in styles)
    print('doc styles english lang remains:', bool(re.search(r'<w:lang[^>]*(?:en|en-US)', styles)))
```
