# RXPNameFixer — Companion Addon Pattern

## Overview
RXPNameFixer is a companion addon that hooks into RestedXP to correct NPC names at runtime.
It demonstrates the pattern of enhancing another addon without modifying its source code.

## Key Patterns

### 1. Hook another addon's update cycle
```lua
hooksecurefunc(addon, "UpdateStepText", function(self)
    C_Timer.After(0.1, FixCurrentStep)  -- run AFTER addon finishes
end)
```

### 2. Hook macro generation (EditMacro)
```lua
EditMacro = function(macroID, name, icon, body, ...)
    if name == "RXPtargeting" then
        body = FixMacroContent(body)  -- correct names in /targetexact
    end
    return origEditMacro(macroID, name, icon, body, ...)
end
```

### 3. NPC name resolution via GameTooltip
```lua
local tooltip = CreateFrame("GameTooltip", "MyTooltip", nil, "GameTooltipTemplate")
tooltip:SetOwner(WorldFrame, "ANCHOR_BOTTOMRIGHT")
tooltip:ClearLines()
tooltip:SetHyperlink(string.format("unit:Creature-0-0-0-0-%d", npcID))
if tooltip:IsShown() then
    local name = _G["MyTooltipTextLeft1"]:GetText()
    name = name:match("^|c%x%x%x%x%x%x%x%x(.*)|r$") or name
end
tooltip:Hide()
```

### 4. Nameplate scanning for pre-caching
```lua
local nameplates = C_NamePlate.GetNamePlates()
for _, plate in ipairs(nameplates) do
    local unit = plate.namePlateUnitToken
    if unit and UnitExists(unit) and not UnitIsPlayer(unit) then
        local npcID = GetNpcIDFromGUID(UnitGUID(unit))
        local name = UnitName(unit)
        if npcID and name then
            CacheNpcName(npcID, name)
        end
    end
end
```

### 5. SavedVariables for persistent cache
```lua
-- SavedVariables: RXPNameFixerDB
-- Store NPC ID -> name mapping
RXPNameFixerDB[npcID] = name

-- Load on login
for id, name in pairs(RXPNameFixerDB) do
    if type(id) == "number" and type(name) == "string" then
        NameCache[id] = name
    end
end
```

### 6. Error logging with recursion prevention
```lua
hooksecurefunc(DEFAULT_CHAT_FRAME, "AddMessage", function(self, msg, ...)
    if msg and type(msg) == "string" then
        if msg:find("RXP Name Fixer") then return end  -- prevent recursion
        if msg:find("RestedXP") and msg:find("Error") then
            LogEntry("RXP_ERROR", msg:sub(1, 200))
        end
    end
end)
```

## Installation
- Path: `C:\Program Files (x86)\World of Warcraft\_anniversary_\Interface\AddOns\RXPNameFixer\`
- TOC: `## Interface: 11508, 110205, 50502, 120001, 110207`
- Dependencies: `## Dependencies: RXPGuides`
- SavedVariables: `RXPNameFixerDB RXPNameFixerLog`

## Slash Commands
- `/rxpnf` — Statistics (cache size, corrections applied)
- `/rxpnf log` — Last 30 log entries
- `/rxpnf logall` — Full log
- `/rxpnf list` — List cached NPC names
- `/rxpnf clear` — Clear name cache
- `/rxpnf clearlog` — Clear log

## Export Script
`export_npc_names.py` reads SavedVariables and exports NPC names to JSON for use in RXP Translator.
```bash
python export_npc_names.py [path_to_SavedVariables]
```
Default path: `C:\Program Files (x86)\World of Warcraft\_anniversary_\WTF\Account\SavedVariables\RXPNameFixer.lua`
