---
name: rxp-translator
description: RXP Translator V5 - Translates RestedXP WoW addon guides to 9 languages using CMaNGOS as primary source
tags: [wow, translator, restedxp, pyqt5, webview, cmangos]
triggers:
  - rxp translator
  - translate guides
  - restedxp
  - cmangos integration
  - zygor translation
  - zygor guides
  - wow addon localization
  - addon translation difficulty
related_skills:
  - wow-addon-development
  - cmangos-locale-extraction
---

# RXP Translator V5

Translates RestedXP World of Warcraft addon guides from English to 9 languages.
**V5 uses CMaNGOS TBC database as primary source for NPC/item/quest names.**

## Current State (V5)
- Location: `C:\Users\ELY\Desktop\RestedXP Edition\RXP_Translator_V5\`
- GUI: PyQt5 + QWebEngineView (frameless, Chromium embedded)
- Interface: HTML dark theme matching RXP addon style
- Languages: 9 (esES, esMX, ptBR, deDE, frFR, ruRU, koKR, zhTW, zhCN)
- **CMaNGOS as primary source** (48,642+ entries per locale)
- Questie NPCs as fallback
- Built .exe exists in `dist/RXP_Translator_V5/`

## Key Files
- `app.py` — PyQt5 GUI with QWebChannel bridge
- `translate_guides.py` — Translation engine (1400+ lines)
- `RXP_Guide_Translator_ES.html` — HTML interface
- `database/merged_{locale}.json` — Combined CMaNGOS + Questie data
- `database/questie_npcs_{locale}.json` — Questie NPC fallback
- `database/zones_{locale}.json` — Zone translations
- `locales_config.py` — 9-language configuration

## References
- `references/rxpguides-locale-system.md` — RXPGuides addon locale architecture, AceLocale-3.0 system, translation checklist
- `references/rar-extraction-windows.md` — How to extract RAR5 archives on Windows (WinRAR UnRAR.exe)
- `references/v4-to-v5-migration.md` — Migration notes from V4 to V5
- `references/restedxp-internals.md` — RestedXP internal data structures, API, guide format, targeting system
- `references/zygor-localization-architecture.md` — Zygor Guides Viewer locale system, string counts, translation effort analysis
- `references/npc-name-source-reliability.md` — NPC source priority for TBC Anniversary, Wowhead ES fallback, and RXPNameFixer cache contamination guard
- `references/open-source-repo-packaging.md` — how to publish/reorganize RestedXP-Traslation V5 as the main open-source translator repo, with RXPNameFixer as optional companion

## Architecture (V5 Priority Order)
For static DB loading, V5 historically loads CMaNGOS first, then Questie data. For **NPC names used by target macros**, prefer exact client/ID correctness over broad coverage:

1. **Manual/client-verified overrides** → Always win
2. **Live WoW client via RXPNameFixer** → Most exact source for displayed NPC names; guard against pet/custom-name contamination
3. **Wowhead TBC Classic localized page by NPC ID** → Best external fallback (`https://www.wowhead.com/tbc/es/npc=<id>`)
4. **QuestieDB** → Best local static source for NPC IDs + localized names
5. **RXPGuides NPCnames / Questie NPCs** → Useful fallback, incomplete
6. **CMaNGOS merged locale data** → Broad fallback; not always best for RXP target-name correctness
7. **Google/MyMemory** → Free text only, never authoritative entity names

See `references/npc-name-source-reliability.md` before changing NPC priority logic.

## Merged Database Format
`merged_{locale}.json` structure:
```json
{
  "questie_npcs": {"English Name": "Translated Name", ...},
  "cmangos_creatures": {"id": "Translated Name", ...},
  "cmangos_items": {"id": "Translated Name", ...},
  "cmangos_quests": {"id": "Translated Name", ...},
  "cmangos_gameobjects": {"id": "Translated Name", ...}
}
```

## LocalDatabase Loading (V5)
In `translate_guides.py`, `LocalDatabase.__init__()`:
1. Loads `merged_{locale}.json` first
2. Adds CMaNGOS entries with `source: "cmangos"` tag
3. Loads Questie NPCs as fallback
4. Questie does NOT overwrite entries already tagged `source: "cmangos"`

## V5 Build Process
1. Copy V4 structure to `RXP_Translator_V5/`
2. Copy `database/merged_*.json` files (CMaNGOS + Questie combined)
3. Modify `translate_guides.py` to load CMaNGOS first
4. Update version strings (V4 → V5) in `app.py`, `translate_guides.py`, HTML
5. Update `build_exe.bat` for V5 naming
6. Run `build_exe.bat` to compile .exe with PyInstaller

## Critical Rules
- Never translate `<<` conditionals (addon logic)
- Never translate `.goto` zone names (addon resolves by English name)
- **Never translate `.zoneskip` / `.subzoneskip` zone names** (same as `.goto` — RestedXP resolves by English name via `addon.GetMapId()`)
- Preserve `|r` count in RXP color tags
- Escape backslashes in regex patterns from zone data
- CMaNGOS names are already translated — use as-is, don't re-translate

## Command Translation Rules
| Command | What to translate | What NOT to translate |
|---------|------------------|----------------------|
| `.goto Zone,x,y` | Text after `>>` | Zone name, coordinates |
| `.zoneskip ZoneName` | Text after `>>` (if any) | Zone name |
| `.subzoneskip ZoneName` | Text after `>>` (if any) | Zone name |
| `.mob NPCName::ID` | NPC name (via database) | NPC ID |
| `.target NPCName::ID` | NPC name (via database) | NPC ID |
| `.unitscan NPCName::ID` | NPC name (via database) | NPC ID |
| `#name Zone Name` | Zone name (via translate_zone_names) | — |
| `#next Zone Name` | Zone name (via translate_zone_names) | — |

## WoW Addon Localization Analysis (Generic Methodology)
When asked to assess translation difficulty for ANY WoW addon, follow this checklist:

### Step 1: Find the localization framework
- Search for `GetLocale()`, `AceLocale`, `LibBabble`, or custom `L()` / `L[]` patterns
- Check for `Localization/` or `locale/` folders with per-locale files
- Read the base/fallback file to understand how missing translations are handled

### Step 2: Count existing coverage per locale
```bash
wc -l Localization/Core_xxXX.lua   # UI strings
wc -l Localization/Quests_xxXX.lua # quest ID→name
wc -l Localization/NPCs_xxXX.lua   # NPC ID→name
```
Compare against the enUS reference file to get coverage %.

### Step 3: Categorize content by translation method
| Category | Example | Method |
|----------|---------|--------|
| UI strings (buttons, labels, tooltips) | Core_xxXX.lua | Manual translation |
| Quest names | Quests_xxXX.lua | Can be auto-extracted from game client via tooltip scanner |
| NPC names | NPCs_xxXX.lua | Can be auto-extracted via `GameTooltip:SetHyperlink("unit:Creature-0-0-0-0-"..id)` |
| Item types/subtypes | Uses `C_Item.GetItemClassInfo()` | Auto-translated by WoW client |
| Guide text (tips, instructions) | Hardcoded in guide .lua files | Manual — largest volume, hardest |
| Spell/ability names | `GetSpellInfo()` | Auto-translated by WoW client |

### Step 4: Quantify guide content (if applicable)
```bash
grep -rch '|tip ' Guides/         # user-visible tips
grep -rch 'accept ' Guides/       # quest accept lines
grep -rch 'kill ' Guides/         # kill objective lines
grep -rch 'talk ' Guides/         # NPC interaction lines
grep -rn '[a-zA-Z]' Guides/ | wc -l  # total lines with English text
```

### Step 5: Assess difficulty tiers
- **Easy**: UI strings with existing localization framework (just translate values)
- **Medium**: Quest/NPC names (can auto-extract from game client or use CMaNGOS)
- **Hard**: Guide text content (narrative tips, instructions — manual work, huge volume)

### Key architectural patterns found in addons:
- **RXP (RestedXP)**: AceLocale-3.0 with `L["key"]` and `L("text")` patterns, separate `locale/` folder
- **Zygor**: Custom `ZygorGuidesViewer_L("name", "locale", data)` with `Core_xxXX.lua` (UI), `Quests_xxXX.lua` (quests), `NPCs_xxXX.lua` (NPCs). Fallback.lua returns English for missing locales. Guides are hardcoded DSL text with no i18n layer.

## Addon Interface Translation (RXPGuides UI)
The addon uses **AceLocale-3.0** for localization. To translate the addon interface:

### Files to modify/create:
1. **`locale/{locale}.lua`** — Translation file (e.g., `esES.lua`, `esMX.lua`)
   - Must include: bindings, `L.delimiter = ' '`, `L.words = {...}`, and ALL `L["key"] = "value"` pairs
   - **Source strings come from TWO places** (not just localization_strings.lua):
     - `locale/localization_strings.lua` — `L["key"] = "value"` pairs (~370 strings)
     - **ALL `.lua` files in addon root + `UI/`** — `L("text")` calls (~493 additional strings)
     - `SettingsPanel.lua` alone has 264 L() calls, `functions.lua` has 98
   - The file needs bindings for Item/Target frames at the top
2. **`locale/locales.xml`** — Add `<Script file="{locale}.lua"/>` line
3. **`Locale.lua`** — Add `or locale == '{locale}'` to the supported languages check (line ~50)

### String extraction (CRITICAL — scan ALL files)
```python
import re
from pathlib import Path

all_strings = {}

# Source 1: localization_strings.lua (L["key"] = "value")
content = (addon_path / "locale" / "localization_strings.lua").read_text(encoding="utf-8-sig")
pattern = r'L\["([^"]+)"\]\s*=\s*"((?:[^"\\]|\\.|"")*)"'
for key, value in re.findall(pattern, content, re.DOTALL):
    all_strings[key] = value

# Source 2: ALL .lua files (L("text") calls)
for lua_file in addon_path.glob("*.lua"):
    fc = lua_file.read_text(encoding="utf-8-sig", errors="ignore")
    for match in re.finditer(r'L\("([^"]+)"\)', fc):
        text = match.group(1)
        if text not in all_strings:
            all_strings[text] = text

# Source 3: UI/*.lua files too
for lua_file in (addon_path / "UI").glob("**/*.lua"):
    fc = lua_file.read_text(encoding="utf-8-sig", errors="ignore")
    for match in re.finditer(r'L\("([^"]+)"\)', fc):
        text = match.group(1)
        if text not in all_strings:
            all_strings[text] = text
```
**Without scanning source files, ~60% of addon UI stays in English.**

### Translation file structure (esES.lua as template):
```lua
local addonName, addon = ...
local L = LibStub("AceLocale-3.0"):NewLocale(addonName, "esES", false)
if not L then return end

-- Binding names (12 total: 4 item + 4 friendly target + 4 enemy target)
_G["BINDING_NAME_" .. "CLICK RXPItemFrameButton1:LeftButton"] = "Objeto activo 1"
-- ... (12 bindings total)

L.delimiter = ' '
L.words = { ["Accept"] = "Acepta", ["Kill"] = "Mata", ["Talk to"] = "Habla con", ... }

-- All strings from localization_strings.lua translated
L["Give Feedback for step"] = "Enviar comentarios sobre este paso"
-- ... (~370+ strings)
```

### esMX handling:
- esMX is a COPY of esES.lua with only line 5 changed: `"esMX"` instead of `"esES"`
- esMX does NOT exist in the original addon — must be created AND registered in locales.xml + Locale.lua

### Key pitfalls:
- The original `esES.lua` is only 110 lines (incomplete). The full translation needs ALL ~400 strings
- `localization_strings.lua` has strings with `%s`, `%d`, `%.0f%%` — preserve format specifiers
- Strings with `|c...|r` color codes must be preserved as-is
- Some strings have `\\n` (literal newline in Lua) — preserve these
- The `L.words` table is used for lazy word-by-word translation of unstored phrases
- After creating the locale file, `locales.xml` and `Locale.lua` MUST be updated or the addon ignores the new locale
- Also scan Lua call sugar `L"text"` / `L'text'`, not only `L("text")`; RXPGuides uses it for step text, map arrow labels (`Step `), tooltips, Active Items/Targets, and skipped-step messages.
- Some visible UI text is hardcoded without locale wrappers. Patch minimal visible strings to use `L"..."` before extracting/generating locales (examples found: `Options...`, `Notable Items:`, `(Click to view)`, `\nUnavailable in combat.`, `Audit`). Do NOT localize frame names, texture paths, macros, enum tokens, or guide DSL.
- Add `## Title-esES`, `## Title-esMX`, `## Notes-esES`, `## Notes-esMX` to every `RXPGuides*.toc`, not just the main TOC, so the addon list is localized for all client variants.
- Keep `esMX.lua` identical to `esES.lua` except the `NewLocale(..., "esMX", ...)` line unless a Mexico-specific wording difference is deliberately requested.

### Verification helper:
- `scripts/verify_rxpguides_ui_locale.py` — copy/run from the addon root after UI localization: `python scripts/verify_rxpguides_ui_locale.py esES esMX`. It checks extracted root/UI locale keys, placeholder preservation, color marker counts, `locales.xml`, `Locale.lua` registration, and quote balance.

## UI i18n System (HTML/JS)
The interface uses `data-i18n` attributes on HTML elements, with a JS `applyLang()` function.
**CRITICAL**: Use `el.textContent` (NOT `el.innerHTML`) for simple labels. `innerHTML` breaks the DOM when elements contain child nodes (selects, buttons with nested spans). Only use `innerHTML` inside the help modal (`#helpModalContent`).

```javascript
function applyLang(selectedLang) {
    const dict = translations[selectedLang];
    if (!dict) return;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (!dict[key]) return;
        if (el.closest('#helpModalContent')) {
            el.innerHTML = dict[key];
        } else {
            el.textContent = dict[key];
        }
    });
}
```

The addon interface section has its OWN language selector (`addonLangSelect`) separate from the guide translation selector (`targetLangSelect`). Don't reuse `targetLangSelect` for addon translation.

## UI Sizing
- Window: 480×620px (compact), min 460×550
- HTML `.window` width: 480px
- Log box: 60px height, 11px font
- Checkboxes: 12px font, 4px padding
- Buttons: 12px font, 6px padding
- Panel padding: 6px 8px
- Content gap: 6px

## Runtime NPC Name Correction (RXPNameFixer Addon)
Static database translations (CMaNGOS, Questie) can't guarantee exact name matches with the game client.
The **RXPNameFixer** companion addon corrects names at runtime using the game client's own data.

### How it works:
1. Hooks `addon.UpdateStepText` via `hooksecurefunc`
2. Extracts NPC IDs from the active step's `.mob`, `.target`, and `.unitscan` data (`element.unitlist`, `element.mobs`, `element.targets`, `element.unitscan`)
3. Uses `GameTooltip:SetHyperlink("unit:Creature-0-0-0-0-"..id)` to get the REAL name from the game client
4. Replaces wrong names in `element.text` and the step's unit lists with correct names
5. Intercepts RestedXP targeting macros (`EditMacro`) and, when name-only matching fails, falls back to the first NPC ID in the current step before writing `/targetexact`
6. Also scans nameplates (`C_NamePlate.GetNamePlates()`) and targets to pre-cache NPC names
7. Saves all names to `SavedVariables` (persistent across sessions)
8. **Never cache player-controlled units** (`UnitPlayerControlled(unit)`) — hunter pets/demons can reuse NPC creature IDs but expose custom names, corrupting translations

### Runtime correction rule of thumb
Do **not** try to repair translated NPC names by fuzzy/free-text matching. Use the current RestedXP step as ground truth: `addon.currentGuide.steps[RXPCData.currentStep]` → NPC IDs → client tooltip localized name. If the ID is unavailable or ambiguous, leave the name unchanged and log it; wrong automatic replacement is worse than English text.

### RestedXP internal APIs used:
- `addon.UpdateStepText(self)` — called when step text changes (hooked via hooksecurefunc)
- `addon.GetNpcName(id)` — RestedXP's own NPC name resolver (GameTooltip trick)
- `RXPCData.currentStep` — current step index
- `addon.currentGuide.steps[i]` — step data with `.elements[]` array
- `element.text` — the display text (can be modified at runtime)
- `element.npcId` / `element.unitlist` — NPC IDs from .mob commands
- `.mob` format: `MobName::NPCID` (e.g., `Filibustero de los Mares del Sur::2545`)

### Key patterns for hooking RestedXP:
```lua
-- Hook step text updates
hooksecurefunc(addon, "UpdateStepText", function(self)
    C_Timer.After(0.1, FixCurrentStep)
end)

-- Access current step data
local step = addon.currentGuide.steps[RXPCData.currentStep]
for _, element in ipairs(step.elements or {}) do
    -- element.text, element.npcId, element.unitlist
end

-- Get NPC name from game client (RestedXP's own method)
GameTooltip:SetOwner(WorldFrame, "ANCHOR_BOTTOMRIGHT")
GameTooltip:ClearLines()
GameTooltip:SetHyperlink(string.format("unit:Creature-0-0-0-0-%d", npcID))
local name = GameTooltipTextLeft1:GetText()
```

### Installation:
- Addon at: `C:\Program Files (x86)\World of Warcraft\_anniversary_\Interface\AddOns\RXPNameFixer\`
- TOC Interface: `11508, 110205, 50502, 120001, 110207` (matches RestedXP)
- Export script: `export_npc_names.py` reads SavedVariables → JSON for RXP Translator

### RXPGuides timer self-anchor bug

Current RXPGuides `Timers.lua` can throw:

```text
Action[SetPoint] failed because[Cannot anchor to itself]
Timers.lua:61 in SortTimers
```

Root cause: `LibCandyBar` reuses hidden frames while `BarContainer.bars` can retain multiple labels pointing to the same frame. `SortTimers()` inserts the same frame twice, then the second occurrence calls `bar:SetPoint(..., lastBar, ...)` where `bar == lastBar`.

Robust fix has three layers:

1. Deduplicate `BarContainer.bars` by frame identity in `SortTimers()` and remove stale labels, preferring the label equal to `bar:GetLabel()`.
2. Guard layout with `if lastBar and bar ~= lastBar then`.
3. In `StartTimer()`, before assigning `BarContainer.bars[label] = bar`, remove every other label still pointing to the reused frame.

This is an RXPGuides timer-manager bug, not an RXPNameFixer macro/name bug. RXPNameFixer does not create CandyBars or call `StartTimer`; extra layout refreshes can merely expose duplicate state sooner. Validate patched `Timers.lua` with `luaparse`. Keep backup because RXPGuides updates may overwrite the patch.

### v2.4 low-priority `*` prefix must be idempotent

RXPGuides uses a leading `*` as an internal low-priority marker. Its `Targeting.lua:FilterList()` removes exactly one marker before processing. A companion bug that strips only `+` but then preserves `*` by prepending another marker causes exponential/linear ticker pollution:

```text
*Darkcrest Slaver → **Darkcrest Slaver → ***Darkcrest Slaver → ...
```

Safe normalization:

```lua
local function StripEntry(value)
    local name = value:match("^[%+%*]*(.+)::%d+$") or value
    return name:gsub("^[%+%*]+", "")
end

local function PreserveLowPriority(value, fixed)
    if fixed and type(value) == "string" and value:match("^%*+") then
        return "*" .. fixed -- maximum one
    end
    return fixed
end
```

Apply this consistently to both active-step lists and lists returned by `GetCurrentTargets()`. Regression invariant: running correction repeatedly on `*****Name` always returns `*Name`, never adds a marker.

### v2.3 never map the last incomplete mob to an arbitrary target

Critical failure discovered in v2.2: when RestedXP removed completed mobs from its active target list, only one incomplete candidate remained. The heuristic `if #candidates == 1 then map it to the current target` corrupted identities whenever the player targeted an already-completed or unrelated NPC:

```text
Médico brujo de Umbrapantano → Vidente de Umbrapantano
Vidente de Umbrapantano → Oráculo de Umbrapantano
```

Required safeguards:

1. Never infer identity from "only one candidate remains".
2. Different first entity tokens may map only when an exact embedded NPC ID proves identity.
3. Same-first-token typo repair (`Vidente ...` → `Vidente ...`) may use high-confidence matching.
4. Mouseover and nameplates only populate `ID → real client name` cache; they must never create full-name overrides.
5. At startup, purge persisted full-name overrides whose first entity token differs, before applying anything to step lists or macros.
6. On reload, RestedXP reconstructs fresh step/list state from guide files; the purge prevents old corrupt SavedVariables from re-corrupting it.

### v2.2 shared typo propagation

A correction may apply to a family of active targets, not only one full NPC name. Verified example:

```text
RXP:    Médico brujo de Umbropantano
Client: Médico brujo de Umbrapantano
```

Learning only the full-name pair fixes Médico but leaves `Vidente de Umbropantano` and `Oráculo de Umbropantano` wrong. When wrong/correct phrases have equal token counts, exactly one differing token, equal byte length, and at most two differing bytes, persist a word-level override and apply it to every target, macro line, and active-step text:

```text
Umbropantano → Umbrapantano
```

Also boost candidate matching when first significant token is exact (`Vidente`, `Oráculo`) so one-character suffix typos clear the confidence threshold. Keep full-name overrides for semantic changes such as `Akoru el Clamafuegos → Akoru el Pirotigma`; do not derive a word override when changed words have different lengths or many differences.

### RXPNameFixer v2.1: obtaining the real RXPGuides object

Another critical distinction in current RXPGuides:

```lua
-- Locale.lua
addon = LibStub("AceAddon-3.0"):NewAddon(addon, addonName, "AceEvent-3.0")

-- RXPGuides.lua
local RXPGuides = {}
addon.RXPGuides = RXPGuides
_G.RXPGuides = RXPGuides
```

`_G.RXPGuides` is only a small public API table. It does **not** contain `targeting`, `RXPFrame`, `generatedSteps`, or internal methods. A companion that uses `_G.RXPGuides` can load and register slash commands while permanently reporting that targeting hooks are unavailable.

Retrieve the real private addon object through AceAddon:

```lua
local AceAddon = LibStub and LibStub("AceAddon-3.0", true)
local addon = AceAddon and AceAddon:GetAddon("RXPGuides", true)
```

With `## Dependencies: RXPGuides`, `Targeting.lua` has already run and `addon.targeting` should exist when the companion loads. Diagnostic invariant after login: `/rxpnf stats` must report `Hooks: OK`, never `Hooks: esperando RXPGuides`.

### RXPNameFixer v2.0 runtime architecture

**Root cause found in RXPGuides `Targeting.lua`:** it captures WoW macro APIs into locals at file load:

```lua
local GetMacroInfo, CreateMacro, EditMacro = GetMacroInfo, CreateMacro, EditMacro
```

Therefore replacing global `EditMacro` from a later-loaded companion addon never intercepts RXP macro writes. Correct integration:

1. `hooksecurefunc(addon.targeting, "UpdateMacro", ...)` then read/rewrite `RXPTargeting` with `GetMacroInfo` + `EditMacro`.
2. Read real private list references via public `addon.targeting.GetCurrentTargets()`.
3. Hook `addon.targeting.UpdateUnitList` and mutate returned list tables before asking RXP to rebuild macro.
4. Traverse `addon.RXPFrame.activeSteps` and `addon.generatedSteps`, not only `addon.currentGuide.steps[RXPCData.currentStep]`.
5. Learn from `PLAYER_TARGET_CHANGED`: exact embedded NPC ID first; otherwise one-candidate or high-confidence token similarity. Avoid blind fuzzy replacement.
6. Create tooltip scanner once; never `CreateFrame` with same global name on every lookup.
7. During combat set pending flag; sync on `PLAYER_REGEN_ENABLED`.
8. Ticker (~0.75s) reapplies overrides so step/zone changes need no `/reload`.

A newly installed code version still needs one initial `/reload` so WoW loads the file; normal runtime corrections afterward do not.

### Historical v1.4 workaround (superseded)

If a screenshot shows the macro UI still has a bad translated `/targetexact` name, do not rely only on the `EditMacro` hook. Add a small manual override and repair the open MacroFrame too:

```lua
local ManualNameFixes = {
    ["Akoru el Clamafuegos"] = "Akoru el Pirotigma",
}

-- WoW Lua compatibility: use strtrim(targetName), not targetName:trim().
-- Periodic ticker can call FixOpenMacroFrame() to patch MacroFrameText and then EditMacro().
```

This is a surgical fallback for known bad DB translations when the current RestedXP step does not expose a reliable NPC ID.

### Key v1.3+ helper functions
```lua
-- Extract NPC ID from "Name::12345", "12345", or number
local function ExtractNpcID(value) ... end

-- Extract NPC name from "+Name::12345" or "Name::12345"
local function ExtractNpcName(value) ... end

-- Get current active step from RestedXP
local function GetCurrentStep()
    return addon.currentGuide.steps[RXPCData.currentStep]
end

-- Iterate all NPC entries in current step's unitlists
local function ForEachCurrentStepNpc(callback)
    -- callback(npcID, oldName, element, list, index)
    -- checks element keys: unitlist, mobs, targets, unitscan
end

-- Get first NPC ID from current step (fallback for macro fix)
local function FirstCurrentStepNpcID() ... end

-- Escape Lua pattern special chars for gsub replacement
local function EscapePattern(text)
    return tostring(text):gsub("([%(%)%.%%%+%-%*%?%[%]%^%$])", "%%%1")
end
```

### RestedXP step element NPC data keys
When iterating `step.elements[]`, NPC data lives in these keys (all checked by `ForEachCurrentStepNpc`):
- `element.unitlist` — populated by `.mob`, `.target`, `.unitscan` commands
- `element.mobs` — from `.mob` command
- `element.targets` — from `.target` command
- `element.unitscan` — from `.unitscan` command

Values are strings like `"MobName::NPCID"` or `"NPCID"` (numeric string). After `CheckNpcIds()` runs, non-English clients may have the name portion stripped, leaving just the ID string.

### GitHub backup / publishing
- Main repo: `https://github.com/eygelias/RestedXP-TraslationV5` (public)
- Local workspace: `C:\Users\ELY\Desktop\COSAS\RestedXP-TraslationV5`
- Release pattern: tag `v5.x.x` with Windows zip asset from `dist/RXP_Translator_V5/*`
- Keep `RXPNameFixer` under `addon_companion/RXPNameFixer/` so the repo remains focused on the guide translator
- Do not commit unrelated artifacts such as Hermes UI zips or private/commercial RestedXP guide files
- See `references/open-source-repo-packaging.md` before reorganizing/publishing the repo

## Pitfalls
- Zone names ending with `\\` break regex — must escape before `re.sub()`
- `|r` count must match between original and translated lines
- PyQt5 `WA_TranslucentBackground` needed for truly frameless window
- CMaNGOS SQL files are large (45+ MB) — load into memory carefully
- SQL `\'` is escaped quote, not backslash-quote
- Multiple INSERT statements per table — parser must handle all of them
- `merged_{locale}.json` must be copied to `database/` folder before building .exe
- **i18n innerHTML bug**: Using `el.innerHTML` on `[data-i18n]` elements replaces child nodes (select options, nested spans). Always use `el.textContent` for non-modal elements.
- **Addon section language selector**: Must have its own `<select id="addonLangSelect">`, NOT reuse `targetLangSelect`
- **localization_strings.lua regex**: Use `r'L\["([^"]+)"\]\s*=\s*"((?:[^"\\]|\\.|"*)*)"'` with `re.DOTALL` to handle multiline values and escaped quotes. The simpler `r'L\["([^"]+)"\]\s*=\s*"([^"]*)"'` misses strings with escaped quotes.
- **deep_translator encoding**: Use `utf-8-sig` encoding when reading Lua files (handles BOM). Also escape `\\` and `"` in translated values before writing.
- **RAR5 on Windows**: Standalone 7z (7zr.exe) does NOT support RAR5. Use `C:\Program Files\WinRAR\UnRAR.exe` instead.
- **`.zoneskip` in guides**: RestedXP resolves `.zoneskip` zone names via `addon.GetMapId()` which expects English names. Never translate zone names in `.zoneskip` or `.subzoneskip` commands. Some guides have typos (e.g., `Stranglethon Vale` instead of `Stranglethorn Vale`) — these cause "map name/ID" errors. The translator should NOT fix these typos.
- **AddMessage hook recursion**: When hooking `DEFAULT_CHAT_FRAME.AddMessage` for logging, filter out your own addon's messages to prevent infinite recursion that fills the log with thousands of entries per second.
