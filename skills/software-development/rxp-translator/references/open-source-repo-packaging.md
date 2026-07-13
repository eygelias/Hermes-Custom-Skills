# Open-source repo packaging for RestedXP-Traslation V5

Use when publishing or reorganizing the project repository.

## Project focus

The public repo should present **RestedXP-Traslation V5** as the main product: a translator for RestedXP/RXPGuides guide `.lua` files. `RXPNameFixer` is a companion addon only, not the main focus.

## Recommended repo layout

```text
README.md
LICENSE
requirements.txt
app.py
translate_guides.py
build_database.py
validate_output.py
translate_addon_interface.py
locales_config.py
RXP_Guide_Translator_ES.html
build_exe.bat
database/
rxpguides_locale/
docs/DATABASE_SOURCES.md
addon_companion/RXPNameFixer/
input/.gitkeep
output/.gitkeep
```

Avoid putting unrelated artifacts in this repo (e.g. Hermes UI translation zips). Keep them in their own repo/context.

## README content checklist

- Lead with: “translator for RestedXP/RXPGuides guide files.”
- Explain what gets translated: tips, guide instructions, NPC/item/object/quest names when safe.
- Explain what must stay untouched: `.goto`, `.zoneskip`, `.subzoneskip` zone names, IDs, coordinates, `<<` conditionals, color tags.
- Include step-by-step tutorial:
  1. Download release or clone repo.
  2. Install `requirements.txt` for source mode.
  3. Prepare/update databases.
  4. Put original guides in `input/`.
  5. Run GUI (`python app.py`) or console (`python translate_guides.py esES`).
  6. Validate output.
  7. Copy translated guides into RXPGuides.
  8. Optional: install `addon_companion/RXPNameFixer` for runtime NPC-name edge cases.
- Link database sources from `docs/DATABASE_SOURCES.md`.
- State that private/commercial RestedXP guide files and credentials should not be committed.

## Database source docs checklist

Document these links:

```text
QuestieDB:  https://github.com/Questie/QuestieDB/releases
RXPGuides:  https://github.com/RestedXP/RXPGuides/releases
CMaNGOS:    https://github.com/cmangos/tbc-db
TBC-DB:     https://github.com/TBC-DB/Database
Questie:    https://github.com/Questie/Questie/releases
Wowhead:    https://www.wowhead.com/tbc/es/npc=<ID>
```

Recommended source priority:

```text
manual_overrides.json > client verified cache > Wowhead TBC ES by ID > QuestieDB > RXPGuides NPCnames > CMaNGOS/TBC-DB > leave English + report unresolved
```

## Release checklist

- Commit source/docs first.
- Run syntax check:

```bash
python -m py_compile app.py translate_guides.py build_database.py validate_output.py translate_addon_interface.py locales_config.py addon_companion/RXPNameFixer/export_npc_names.py
```

- Create Windows zip from `dist/RXP_Translator_V5/*` as release asset.
- Create/update GitHub release, e.g. `v5.0.0`, with release notes focused on the translator.
- Tag should point to the final commit containing docs/source updates.
