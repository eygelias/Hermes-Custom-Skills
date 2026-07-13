# Zygor Guides Viewer — Localization Architecture

Addon path: `C:\Users\ELY\Desktop\ZygorGuidesViewerClassicTBCAnniv\`

## Localization System: `ZygorGuidesViewer_L()`

Custom system (NOT AceLocale). Defined in `Localization/Base.lua`:

```lua
function _G.ZygorGuidesViewer_L(name, locale, translations, debug)
    -- Loads translations into data[name] table
    -- enUS sets the base; other locales only override keys they provide
    -- Missing keys fall back to the key name itself (via __index metamethod)
end
```

### Data Categories (each is a separate table):
| Table Name | File Pattern | Content | enUS Lines | esES Lines |
|---|---|---|---|---|
| `Main` | `Core_xxXX.lua` | UI strings, step goals, options, tooltips | 2,267 | 49 (itemscore only) |
| `Quests` | `Quests_xxXX.lua` | Quest ID → localized name | 4,508 | 2,611 |
| `NPCs` | `NPCs_xxXX.lua` | NPC ID → localized name | 4,790 | 2,729 |
| `Specials` | `Core_xxXX.lua` | Plural rules, mob contraction | — | 49 |
| `Guides` | *(empty in enUS)* | Guide text overrides | 0 | 0 |

### Fallback Behavior (`Localization/Fallback.lua`):
```lua
if locale=="enGB" or locale=="enUS" then return end
ZygorGuidesViewer_L("Guides", locale, function() return {} end)
ZygorGuidesViewer_L("Main", locale, function() return {} end)
ZygorGuidesViewer_L("Specials", locale, function() return {
    ["plural"] = function(word) return word end,
    ['contract_mobs'] = false,
} end)
```
Non-English locales that don't have Core_xxXX.lua get empty tables → fallback to English defaults.

### How code accesses translations:
```lua
local L = ZGV.L        -- Main table (UI strings)
local LM = ZGV.LM      -- ?
local LI = ZGV.LI       -- ?
local LC = ZGV.LC       -- ?
local LQ = ZGV.LQ       -- Quests
local LS = ZGV.LS       -- Specials
local DL = ZGV.DL       -- ?
```

Usage: `L['stepgoal_kill']` → "Kill %s" (English) or "Matar %s" (Spanish if translated)

## Core_enUS.lua Sections (2,267 lines)

| Section | Lines | Content |
|---|---|---|
| Global | 17–25 | Font paths, addon name display |
| Step goals | 27–231 | ~200 action templates ("Kill %s", "Accept %s", etc.) |
| Item types | 234–373 | Armor/weapon/consumable types (uses WoW API, auto-translates) |
| Itemscore patterns | 374–415 | Stat parsing regexes |
| Options | 416–848 | ~430 settings labels, descriptions, values |
| Code files | 850–1797 | ~950 strings for BugReport, GuideMenu, Gold, Talents, etc. |
| Colour coding | 1798–2081 | Tooltip color codes and labels |
| Misc strings | 2082–2267 | Catch-all for additional translations |

## Guide Content (NOT localized — hardcoded English)

Guide files are in `Guides-TBC/` (184,711 lines, 56 MB total). They use a custom DSL:
```
step
talk Brother Danil##152
Sell Items |vendor Brother Danil##152 |goto Elwynn Forest/0 47.49,41.56
|tip Outside next to the building.
|tip Kill enemies along the way.
Click to continue |confirm
```

### User-visible content breakdown:
| Pattern | Count | Translatable? |
|---|---|---|
| `\|tip` lines | 28,069 | Manual — narrative advice |
| `talk` commands | 12,543 | NPC name via database; action via L[] |
| `accept` commands | 8,067 | Quest name via database; action via L[] |
| `kill` commands | 6,079 | NPC name via database; action via L[] |
| `confirm` lines | 1,356 | Text is user-visible, needs translation |
| Total English text lines | 171,589 | Mostly guide narrative |

### What IS auto-translated at runtime:
- Step goal verbs (Kill, Accept, Talk to) → via `L["stepgoal_kill"]` etc.
- NPC names → via `Localizers:GetTranslatedNPC(id)` which checks tooltip scanner cache
- Quest names → via `Localizers:GetQuestData(qid)` which uses `C_QuestLog.GetQuestInfo()`
- Item types → via `C_Item.GetItemClassInfo()` (WoW client provides localized names)

### What is NOT auto-translated:
- `|tip` text (advice, instructions, narrative)
- Guide section names (e.g., "Human Starter (1-11)")
- `_NOTE:_` blocks
- `_Destroy This Item:_` labels
- Free-text user instructions

## esMX Gap
- `Quests_esMX.lua`: EMPTY (3 lines, no data)
- `Core_esMX.lua`: Only itemscore patterns (49 lines)
- Fix: copy esES → esMX, change locale check on line 1

## Translation Effort Estimate (esES)
| Component | Strings/Lines | Effort |
|---|---|---|
| Core_esES.lua (UI) | ~1,600 missing | 2–3 days |
| Quests_esES.lua gaps | ~1,900 missing | Auto-extractable |
| NPCs_esES.lua gaps | ~2,000 missing | Auto-extractable |
| Guide tips + text | ~172,000 lines | 6–12 months manual |
| Options.lua hardcoded | ~75 strings | 2–3 hours |

## Key Files for Translation Work
- `Localization/Base.lua` — Framework (understand before modifying)
- `Localization/Core_enUS.lua` — Master string list (2,267 lines, copy to esES)
- `Localization/Fallback.lua` — Fallback behavior
- `Localization-TBC/Quests_enUS.lua` — Quest ID reference
- `Localization-TBC/NPCs_enUS.lua` — NPC ID reference
- `Options.lua` — Has ~75 hardcoded English strings not in localization system
- `Goal.lua` (5,002 lines) — Parses guide DSL, uses L[] for step goal verbs
- `Parser.lua` (2,961 lines) — Guide text parser
