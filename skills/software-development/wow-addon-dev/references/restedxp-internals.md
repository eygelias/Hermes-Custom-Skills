# RestedXP Addon Internals

## Overview
RestedXP Guides is a WoW leveling guide addon. It uses a custom guide format with directives like `.mob`, `.goto`, `.zoneskip`, `.accept`, `.turnin`.

## Key Data Structures

### Step data (`addon.currentGuide.steps[i]`)
```lua
step = {
    index = 1,           -- step number
    active = true,       -- is this the current step?
    elements = {         -- array of step elements
        [1] = {
            tag = "mob",           -- element type
            text = "Kill 10 Pirates",  -- display text (mutable!)
            npcId = 1234,          -- NPC ID (for .mob)
            unitlist = {"Pirate", "1234"},  -- mob names/IDs
            mobs = {"Pirate::1234"},       -- raw .mob args
            questId = 5678,        -- quest ID (for .accept/.turnin)
            step = <step_ref>,     -- back-reference to parent step
        }
    }
}
```

### Current step access
```lua
local currentStep = RXPCData.currentStep  -- step index
local step = addon.currentGuide.steps[currentStep]
if step and step.active then
    for _, element in ipairs(step.elements or {}) do
        -- element.text, element.tag, element.npcId, etc.
    end
end
```

## .mob Command Format
The `.mob` directive format is: `.mob DisplayName::NPCID`
- Example: `.mob Filibustero de los Mares del Sur::2545`
- `CheckNpcIds()` parses this: `name, id = v:match("(.+)::(%d+)$")`
- If player language is English, uses the name directly
- Otherwise, tries to resolve ID to localized name via `addon.GetNpcName(id)`
- `UpdateNpcNames()` runs when step becomes active, resolves IDs to names

## Targeting System (Active Targets)
RestedXP's targeting system scans nameplates and marks mobs with raid icons:
- `addon.targeting:CheckNameplate(nameplateID)` — checks a single nameplate
- `addon.targeting:UpdateMacro(queuedTargets)` — generates/updates the targeting macro
- `addon.targeting:UpdateUnitList()` — refreshes the list of targets to scan
- Macro name: `self.macroName` = `"RXPtargeting"`
- Uses `C_NamePlate.GetNamePlates()` for nearby nameplates
- Uses `UnitName(nameplateID)` to get NPC names from nameplates

## NPC Name Resolution
```lua
-- RestedXP's own method (in functions.lua)
function addon.GetNpcName(id)
    local npc = NPCNames[id]  -- cache
    if type(npc) == "string" then return npc end
    if not npc or GetTime()-npc > 1.5 then
        GameTooltip:SetOwner(WorldFrame, "ANCHOR_BOTTOMRIGHT")
        GameTooltip:ClearLines()
        GameTooltip:SetHyperlink(string.format("unit:Creature-0-0-0-0-%d", id))
        if GameTooltip:IsShown() then
            local name = GameTooltipTextLeft1:GetText()
            name = name:match("^|c%x%x%x%x%x%x%x%x(.*)|") or name
            NPCNames[id] = name
            return name
        end
        GameTooltip:Hide()
        NPCNames[id] = GetTime()  -- rate limit
    end
end
```

## Guide Parsing Error Format
When RestedXP can't parse a directive, it calls:
```lua
addon.error(L("Error parsing guide") .. " " .. addon.currentGuideName .. ": map name/ID\n" .. self)
```
This appears in chat as: `RestedXP Guides: Error al analizar la guía X-Y ZoneName: map name/ID\n.directive ZoneName`

Common causes:
- `.zoneskip` with wrong zone name (typo, or localized name instead of English)
- `.goto` with invalid zone name
- Missing zone in `addon.mapId` table

## Map ID System
```lua
addon.GetMapId(zone)  -- returns numeric map ID from English zone name
addon.mapId["Stranglethorn Vale"] = 210  -- example mapping
addon.mapConversion[oldID] = newID  -- version-specific ID conversion
```

## Key Events
- `PLAYER_TARGET_CHANGED` — when player changes target
- `NAME_PLATE_UNIT_ADDED` / `NAME_PLATE_UNIT_REMOVED` — nameplate visibility
- `QUEST_ACCEPTED` / `QUEST_TURNED_IN` / `QUEST_LOG_UPDATE` — quest state
- `ZONE_CHANGED_NEW_AREA` — player entered new zone
- `UPDATE_MOUSEOVER_UNIT` — mouseover a unit

## Useful Globals
- `RXPCData` — persistent saved data (currentStep, settings)
- `addon.currentGuide` — currently loaded guide
- `addon.currentGuideName` — name of current guide
- `addon.settings.profile` — user settings
- `addon.icons` — icon textures for different element types
- `addon.activeTheme` — current UI theme colors
