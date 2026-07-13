# RXPGuides Addon Locale System

## Architecture
RXPGuides uses **AceLocale-3.0** for i18n. The locale system has these components:

### 1. `locale/localization_strings.lua` — Primary string definitions
- ~370+ `L["key"] = "English value"` pairs
- Grouped by source file (Communications.lua, functions.lua, GuideWindow.lua, etc.)
- **NOT the only source!** Many strings are defined via `L("text")` calls in source .lua files

### 1b. Source .lua files — SECONDARY string source (CRITICAL!)
- `SettingsPanel.lua` has 264 `L("text")` calls
- `functions.lua` has 98 `L("text")` calls
- `LevelingTracker.lua` has 51, `GuideWindow.lua` has 20, etc.
- **Total: ~493 additional strings** NOT in localization_strings.lua
- Without scanning these files, ~60% of addon UI stays in English
- Pattern: `L("text")` with parentheses, not brackets

### 2. `locale/{locale}.lua` — Per-locale translations
- Each file registers with `LibStub("AceLocale-3.0"):NewLocale(addonName, "{locale}", false)`
- Contains: bindings, L.delimiter, L.words, and translated L["key"] = "value" pairs
- Only needs strings that DIFFER from English (AceLocale falls back to key for missing entries)

### 3. `locale/locales.xml` — Registration file
- Lists all .lua files to load via `<Script file="..."/>`
- Must include new locale files or they won't load

### 4. `Locale.lua` — Runtime locale detection
- Line ~50 has the supported language check:
  ```lua
  if locale == 'zhCN' or locale == 'zhTW' or locale == 'frFR' or locale == 'koKR' or locale == 'esES' or locale == 'esMX' or locale == 'ruRU' then
  ```
- Missing locales here = addon falls back to English (noop function)

## Translatable components per locale file

### Binding names (12 total)
```lua
_G["BINDING_NAME_" .. "CLICK RXPItemFrameButton1:LeftButton"] = "..."
_G["BINDING_NAME_" .. "CLICK RXPItemFrameButton2:LeftButton"] = "..."
_G["BINDING_NAME_" .. "CLICK RXPItemFrameButton3:LeftButton"] = "..."
_G["BINDING_NAME_" .. "CLICK RXPItemFrameButton4:LeftButton"] = "..."
_G["BINDING_NAME_" .. "CLICK RXPTargetFrame_FriendlyButton1:LeftButton"] = "..."
-- ... 4 friendly + 4 enemy targets
```

### Word table (for lazy translation)
```lua
L.delimiter = ' '
L.words = {
    ["Accept"] = "Acepta", ["Kill"] = "Mata",
    ["Talk to"] = "Habla con", ["Turn in"] = "Entrega",
    ["Collect"] = "Recoge", ["Buy"] = "Compra",
    ["Use"] = "Usa", ["Set"] = "Establece"
}
```
Used by `Locale.lua` to translate phrases word-by-word when exact match not found.

### String categories (from localization_strings.lua)
- **Communications.lua** — Feedback, level-up messages, flying timers
- **functions.lua** — Step actions (Go to, Fly to, Kill, etc.), grind messages
- **GuideLoader.lua** — Loading messages, parse errors
- **GuideWindow.lua** — UI labels, step list, welcome messages
- **SettingsPanel.lua** — ALL settings labels and descriptions (~200+ strings)
- **LevelingTracker.lua** — Time splits, experience tracking
- **InventoryManager.lua** — Junk items, sell messages
- **Targeting.lua** — Target scanning, rare notifications
- **Tips.lua** — Warning messages, danger alerts
- **ItemUpgrades.lua** — Item comparison labels
- **RXPGuides.lua** — Slash command responses

## esES vs esMX
- Original addon has esES only (110 lines, incomplete)
- esMX was created by ChatGPT — identical to esES except locale identifier
- esMX MUST be added to locales.xml AND Locale.lua to work
- In practice, esES and esMX translations are identical (same Spanish)

## Parsing localization_strings.lua
```python
# Simple pattern (misses escaped quotes):
pattern = r'L\["([^"]+)"\]\s*=\s*"([^"]*)"'

# Robust pattern (handles multiline, escaped quotes):
pattern = r'L\["([^"]+)"\]\s*=\s*"((?:[^"\\]|\\.|"")*)"'
strings = re.findall(pattern, content, re.DOTALL)
```

## Parsing source .lua files for L() calls
```python
import re
from pathlib import Path

all_strings = {}

# Source 1: localization_strings.lua
content = (addon_path / "locale" / "localization_strings.lua").read_text(encoding="utf-8-sig")
pattern = r'L\["([^"]+)"\]\s*=\s*"((?:[^"\\]|\\.|"")*)"'
for key, value in re.findall(pattern, content, re.DOTALL):
    if len(value) >= 3:
        all_strings[key] = value

# Source 2: ALL .lua files in addon root
for lua_file in addon_path.glob("*.lua"):
    fc = lua_file.read_text(encoding="utf-8-sig", errors="ignore")
    for match in re.finditer(r'L\("([^"]+)"\)', fc):
        text = match.group(1)
        if len(text) >= 3 and text not in all_strings:
            all_strings[text] = text

# Source 3: UI/*.lua files
for lua_file in (addon_path / "UI").glob("**/*.lua"):
    fc = lua_file.read_text(encoding="utf-8-sig", errors="ignore")
    for match in re.finditer(r'L\("([^"]+)"\)', fc):
        text = match.group(1)
        if len(text) >= 3 and text not in all_strings:
            all_strings[text] = text

print(f"Total unique strings: {len(all_strings)}")
```

## Full translation checklist
1. [ ] Scan ALL .lua files for L() calls (not just localization_strings.lua)
2. [ ] Generate `locale/{locale}.lua` with all ~800+ translated strings
3. [ ] Add bindings (12 total) at top of file
4. [ ] Add `L.delimiter = ' '` and `L.words = {...}`
5. [ ] Add `<Script file="{locale}.lua"/>` to `locale/locales.xml`
6. [ ] Add `or locale == '{locale}'` to `Locale.lua` line ~50
7. [ ] Preserve format specifiers: `%s`, `%d`, `%d%%`, `%.0f%%`
8. [ ] Preserve color codes: `|cff228B22...|r`
9. [ ] Preserve escaped newlines: `\\n`
10. [ ] Test by setting game client to target locale
