# RestedXP Addon Internals (v4.10.14)

## Key Data Structures

### Step System
- `RXPCData.currentStep` — current step index (number)
- `addon.currentGuide.steps[i]` — step array
- `step.active` — boolean, true if step is currently active
- `step.elements` — array of element objects in the step
- `step.index` — step number

### Element Types
Each element has `.tag` identifying its type:
- `mob` — kill mob objective (has `.mobs`, `.unitlist`, `.npcId`)
- `accept` — accept quest (has `.questId`, `.title`)
- `turnin` — turn in quest
- `complete` — quest completion check
- `target` — targeting objective
- `unitscan` — scan for specific units
- `collect` — collect items
- `daily` — daily quest

### Element Fields
```lua
element.text          -- display text (can be modified at runtime)
element.textOnly      -- true for mob/unitscan (no quest tracking)
element.step          -- back-reference to parent step
element.mobs          -- mob ID list (for .mob command)
element.unitlist      -- same as mobs, gets resolved from IDs to names
element.npcId         -- single NPC ID
element.questId       -- quest ID
element.title         -- quest title
element.completed     -- boolean
element.active        -- boolean
element.update        -- boolean, needs name resolution
element.parent        -- parent element (for nested objectives)
```

## .mob Command Format
```
.mob MobName::NPCID;MobName2::NPCID2
```
Example: `.mob Filibustero de los Mares del Sur::2545`

The `CheckNpcIds()` function parses this:
- If `addon.player.lang == "en"` → uses the name part
- Otherwise → tries to resolve ID to name via `addon.GetNpcName(id)`
- If name not found → stores ID as string, sets `element.update = true`

## NPC Name Resolution
```lua
-- RestedXP's method (functions.lua line 850)
function addon.GetNpcName(id)
    local npc = NPCNames[id]  -- cache
    if type(npc) == "string" then return npc end
    if not npc or GetTime()-npc > 1.5 then
        GameTooltip:SetOwner(WorldFrame, "ANCHOR_BOTTOMRIGHT")
        GameTooltip:ClearLines()
        GameTooltip:SetHyperlink(string.format("unit:Creature-0-0-0-0-%d", id))
        if GameTooltip:IsShown() then
            name = GameTooltipTextLeft1:GetText()
            NPCNames[id] = name
            return name
        end
    end
end
```

## Step Text Update Flow
1. Step becomes active → `UpdateStepText(self)` called
2. Sets `addon.updateStepText = true` and `addon.stepUpdateList[index] = true`
3. On next frame update, RestedXP re-renders the step text
4. Elements with `.update = true` get name resolution attempted
5. `UpdateNpcNames(element)` resolves IDs → names in `element.unitlist`
6. BUT `element.text` is NOT automatically updated — only `unitlist`

## Active Targets / Nameplate Scanning
- `Targeting.lua` handles the nameplate scanning system
- `addon.targeting:CheckNameplate(nameplateID)` scans each nameplate
- Uses `UnitName(nameplateID)` to get mob name
- Matches against `element.unitlist` to find guide-relevant mobs
- Marks matching mobs with raid icons (skull, cross, square, moon)
- `addon.targeting:UpdateUnitList()` refreshes the targeting list

## Key Functions
```lua
addon.UpdateStepText(self)     -- triggers step text re-render
addon.GetNpcName(id)           -- resolve NPC ID → name via GameTooltip
addon.GetNpcId(unit, isGuid)   -- extract NPC ID from GUID
addon.GetQuestName(id, element) -- get quest name by ID
addon.ReplaceNpcIds(textLine, element) -- replace npc:NAME:ID patterns
addon.ScheduleTask(delay, func) -- delayed execution
addon.ReloadStep()             -- force step re-render
```

## Accessing from a Companion Addon
```lua
local RXP = _G.RXPGuides
local addon = RXP
local currentStep = RXPCData.currentStep
local step = addon.currentGuide.steps[currentStep]

-- Hook for step text changes
hooksecurefunc(addon, "UpdateStepText", function(self)
    -- self.step has the step data
end)
```

## SavedVariables
- `RXPCData` — per-character settings (currentStep, skipDailies, etc.)
- `RXPDB` — account-wide data
- NPC names are cached in `NPCNames` (local to functions.lua, not SavedVariables)
