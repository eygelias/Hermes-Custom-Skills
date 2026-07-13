---
name: cmangos-locale-extraction
description: Extract and integrate CMaNGOS TBC locale data for RXP Translator
tags: [cmangos, wow, tbc, locale, translation, database]
triggers:
  - cmangos
  - tbc database
  - wowhead extraction
  - locale data
  - creature_template
related_skills:
  - rxp-translator
---

# CMaNGOS TBC Locale Extraction

Extracts localized names from the CMaNGOS TBC database SQL files and integrates them into the RXP Translator.

## Data Source
- Repository: `cmangos/tbc-db` (GitHub)
- File: `locales/OtherLocales.sql` (45.6 MB)
- Contains: `locales_creature`, `locales_item`, `locales_quest`, `locales_gameobject`

## Column Mapping
The SQL table has columns for each locale:
- `name_loc1` = koKR, `name_loc2` = frFR, `name_loc3` = deDE
- `name_loc4` = zhCN, `name_loc5` = zhTW, `name_loc6` = esES
- `name_loc7` = esMX, `name_loc8` = ptBR
- `subname_loc1` through `subname_loc8` for subtitles (Vendor, Trainer, etc.)

## Scripts
- **Extraction**: `extract_cmangos_locales.py` — Parses SQL → `database/cmangos_{locale}.json`
- **Integration**: `integrate_cmangos.py` — Merges CMaNGOS + Questie → `database/merged_{locale}.json`

## Extraction Script Usage
```bash
cd "C:\Users\ELY\Desktop\RestedXP Edition"
python extract_cmangos_locales.py
```

## Integration Script Usage
```bash
python integrate_cmangos.py
```

Creates `merged_{locale}.json` with structure:
```json
{
  "questie_npcs": {"English Name": "Translated Name"},
  "cmangos_creatures": {"id": "Translated Name"},
  "cmangos_items": {"id": "Translated Name"},
  "cmangos_quests": {"id": "Translated Name"},
  "cmangos_gameobjects": {"id": "Translated Name"}
}
```

## SQL Parser Design (v5 — final working version)
The parser must handle:
1. **Multiple INSERT statements** per table (5 for creatures, 8 for items, 29 for quests, 3 for gameobjects)
2. **Escaped quotes** — `\'` in SQL strings
3. **Paren depth tracking** — tuples can contain nested parens
4. **Large file** — 45.6 MB loaded into memory (~36M characters)

Key parsing logic:
```python
# Track paren depth and string state
while i < n and paren_depth > 0:
    ch = values_block[i]
    if in_string:
        if ch == '\\':  # Escaped char
            i += 2; continue
        if ch == "'":   # End of string
            in_string = False
    else:
        if ch == "'":   # Start string
            in_string = True
        elif ch == ',':
            values.append(current); current = ""
        elif ch == '(':
            paren_depth += 1
        elif ch == ')':
            paren_depth -= 1
            if paren_depth == 0:
                values.append(current)
                # Process tuple
```

## Results (as of extraction)
| Locale | Creatures | Items | Quests | Gameobjects | Total |
|--------|-----------|-------|--------|-------------|-------|
| esES | 17,712 | 18,232 | 48 | 12,650 | 48,642 |
| esMX | 17,712 | 18,232 | 48 | 12,649 | 48,641 |
| deDE | 17,814 | 18,233 | 48 | 12,649 | 48,744 |
| ptBR | 18,441 | 18,279 | 48 | 12,894 | 49,662 |
| koKR | 17,933 | 18,236 | 39 | 12,658 | 48,866 |
| zhCN | 17,862 | 18,252 | 42 | 12,901 | 49,057 |
| zhTW | 17,718 | 18,230 | 7 | 12,655 | 48,610 |

## esES vs esMX Separation
CMaNGOS stores esES (column 6) and esMX (column 7) separately. Most entries are identical (Blizzard uses same translation), but differences exist:

| Table | Total Entries | Differences | Examples |
|-------|---------------|-------------|----------|
| creatures | 17,712 | **4** | "Siamés" vs "Siamês", "Zergling" vs "Zerguezno" |
| items | 18,232 | **8** | "Escopeta de conchas" vs "Escopeta lanza caparazones" |
| quests | 48 | **0** | — |
| gameobjects | 12,650 | **1** | "Bola y cadena de Knot" vs "Knots Ball and Chain" |

**Total: 13 differences out of 48,642 entries (0.03%)**

User concern about "mixing" is actually correct behavior — most entries ARE the same because Blizzard uses identical translations for both locales. The extraction correctly separates them using different column indices.

## Verification Scripts
- `check_locales.py` — Checks raw SQL for esES/esMX differences
- `verify_extraction.py` — Verifies extracted JSON files maintain separation
- `verify_full.py` — Full verification across all tables

## Pitfalls
- **No English names in locale SQL**: CMaNGOS locale files only have translations. English names are in `creature_template` (separate file, not in this repo).
- **Large file**: `OtherLocales.sql` is 45.6 MB, ~36M characters in memory.
- **Escaped quotes**: SQL uses `\'` for escaped quotes. Parser must handle `\\` followed by `'`.
- **Multiple INSERT statements**: Each table has multiple INSERT blocks. Parser must iterate ALL of them, not just the first.
- **Filter entries**: Skip entries starting with `[UNUSED]`, `[INUTILISÉ]`, or empty names.
- **Integration priority**: CMaNGOS entries should NOT be overwritten by Questie. Tag with `source: "cmangos"` and check before overwriting.
- **esES/esMX user confusion**: Users may think identical entries mean "mixing" — explain that 99.97% are intentionally the same.
