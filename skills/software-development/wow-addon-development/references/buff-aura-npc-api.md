# Buff/Aura Manipulation API (TBC Classic 2.5.5)

## Canceling Buffs/Auras

### ⚠️ CancelUnitBuff Takes INDEX Not Name
```lua
-- WRONG: CancelUnitBuff("player", "Cat Form")  -- fails silently or errors
-- RIGHT:
for i = 1, 40 do
    local name = UnitBuff("player", i)
    if not name then break end
    if name == "Cat Form" then
        CancelUnitBuff("player", i)  -- index
        break
    end
end
```

### Three Methods for Canceling Shapeshift Forms (in order of preference)
1. `CancelShapeshiftForm()` — direct API, may not exist in all versions
2. `CancelUnitBuff("player", buffIndex)` — iterate buffs, find by name, cancel by index
3. `CancelPlayerBuff(buffIndex)` — Classic-era API fallback
4. `RunMacroText("/cancelaura <name>")` — macro approach, most reliable

Always wrap each in `pcall()`. The macro approach is the most reliable fallback.

## Druid Form Buff Names

### English
| Form | Buff Name |
|------|-----------|
| Cat | "Cat Form" |
| Bear | "Bear Form" |
| Dire Bear | "Dire Bear Form" |
| Travel | "Travel Form" |
| Aquatic | "Aquatic Form" |
| Moonkin | "Moonkin Form" |
| Tree of Life | "Tree of Life" |

### Spanish (Español)
| Form | Buff Name |
|------|-----------|
| Cat | "Forma de felino" |
| Bear | "Forma de oso" |
| Dire Bear | "Forma de oso temible" |
| Travel | "Forma de viaje" |
| Aquatic | "Forma acuatica" |
| Moonkin | "Forma de lechuciclo" |

**Detection**: `GetShapeshiftForm()` returns 0 (human) or 1+ (any form). Use as primary check, buff scan as backup.

## NPC Interaction API

### Events That Fire on NPC Interaction
- `GOSSIP_SHOW` — general dialog
- `MERCHANT_SHOW` — vendors
- `TAXIMAP_OPENED` — flight masters
- `TRAINER_SHOW` — class/profession trainers
- `BANKFRAME_OPENED` — bank
- `QUEST_GREETING` — quest list
- `QUEST_DETAIL` / `QUEST_PROGRESS` / `QUEST_COMPLETE` — quest frames
- `PETITION_SHOW` — guild petitions

### Gossip Frame API (TBC Anniversary)
```lua
-- Get gossip options
local opts = C_GossipInfo.GetOptions()
-- Each opt: { name, icon, gossipOptionID, ... }

-- Select option (TBC Anniversary: gossipOptionID is the 1-based index)
C_GossipInfo.SelectOption(opts[1].gossipOptionID)

-- Fallback: click the gossip frame buttons directly
for i = 1, 20 do
    local btn = _G["GossipTitleButton" .. i]
    if btn and btn:IsVisible() and btn:IsEnabled() then
        btn:Click()
        break
    end
end
```

### Protected NPC Interaction Functions
- `InteractUnit("target")` — PROTECTED, cannot be called from addon code
- `TargetUnit("target")` — PROTECTED in combat, restricted out of combat
- `SecureActionButton:Click()` does NOT provide hardware input context for protected functions
- **Workaround**: Use `RunMacroText("/targetexact Name")` to retarget, then inform user to click NPC manually
