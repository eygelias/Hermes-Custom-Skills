# V4 → V5 Migration Guide

## What Changed
V5 replaces Questie NPCs as primary source with CMaNGOS TBC database.

## Files Changed
1. `translate_guides.py` — `LocalDatabase.__init__()` loads `merged_{locale}.json` first
2. `app.py` — Version strings updated to V5
3. `RXP_Guide_Translator_ES.html` — Title and help text updated to V5
4. `build_exe.bat` — Target name changed to `RXP_Translator_V5`
5. `database/merged_*.json` — New files with CMaNGOS + Questie combined

## Key Code Change in translate_guides.py
```python
# V5: Load merged data (CMaNGOS primary)
merged_file = DATABASE_DIR / f"merged_{locale}.json"
merged_data = load_json(merged_file, {})

# Add CMaNGOS creatures with source tag
for cid, name in cmangos_creatures.items():
    if name and not name.startswith("["):
        npc_id = f"cmangos_{cid}"
        npcs_section[npc_id] = {
            "en": name,
            locale: name,
            "source": "cmangos",
            "cmangos_id": cid
        }

# Questie only updates entries NOT from CMaNGOS
for npc_id, npc_data in matches:
    if npc_data.get("source") != "cmangos":
        npc_data[locale] = trans_name
```

## Build Steps
```bash
cd "C:\Users\ELY\Desktop\RestedXP Edition\RXP_Translator_V5"
./build_exe.bat
```

Output: `dist/RXP_Translator_V5/RXP_Translator_V5.exe`

## Distribution
Copy entire `dist/RXP_Translator_V5/` folder. Contains:
- `RXP_Translator_V5.exe`
- `_internal/` (Python runtime + dependencies)
- `database/` (merged JSON files)
- `cache/` (translation cache)
- `icon.ico`
