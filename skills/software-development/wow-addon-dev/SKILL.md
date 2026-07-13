---
name: wow-addon-dev
description: "WoW addon development for TBC Classic Anniversary 2.5.5 (Interface 20505). Covers API pitfalls, config panels, nameplate hooking, combo points, SavedVariables, color pickers, sliders, and safe frame creation."
triggers:
  - "wow addon"
  - "world of warcraft addon"
  - "tbc classic addon"
  - "wow lua"
  - "wow api"
  - "combo points nameplate"
  - "wow interface 20505"
  - "wow classic addon development"
  - "restedxp internals"
  - "wow companion addon"
related_skills:
  - wow-addon-development
references:
  - references/restedxp-internals.md — RestedXP internal data structures, API, guide format
  - references/rxpnamefixer-addon.md — Companion addon pattern (hooking, EditMacro, logging)
---

# WoW Addon Development — TBC Classic Anniversary 2.5.5

Interface version: `20505`. Addons path: `C:\Program Files (x86)\World of Warcraft\_anniversary_\Interface\AddOns`

## Critical API Pitfalls (TBC Anniversary 2.5.5)

These are confirmed broken or changed in TBC Anniversary 2.5.5. Violating them causes silent failures or runtime errors.

### 1. `SetBackdrop` requires BackdropTemplate
```lua
-- BROKEN: orb.border = CreateFrame("Frame", nil, parent)
-- FIXED:
orb.border = CreateFrame("Frame", nil, parent, "BackdropTemplate")
orb.border:SetBackdrop({edgeFile = "...", edgeSize = 10, insets = {...}})
```
Any frame calling `SetBackdrop` or `SetBackdropBorderColor` MUST inherit `"BackdropTemplate"`.

### 2. `InterfaceOptions_AddCategory` is broken
TBC Anniversary silently ignores `InterfaceOptions_AddCategory`. Use the Settings API:
```lua
if Settings and Settings.RegisterCanvasLayoutCategory then
    local category = Settings.RegisterCanvasLayoutCategory(panel, panel.name)
    category.ID = panel.name
    Settings.RegisterAddOnCategory(category)
    ns.optionsCategory = category
else
    InterfaceOptions_AddCategory(panel)  -- fallback for Classic Era
end
```
Open with: `Settings.OpenToCategory(ns.optionsCategory:GetID())`

### 3. `OptionsSliderTemplate` has no visible track
Use `MinimalSliderTemplate` with atlas textures (same as Leatrix Plus):
```lua
local slider = CreateFrame("Slider", name, parent, "MinimalSliderTemplate")
slider:SetThumbTexture(thumb)  -- thumb created with atlas
-- Track textures:
local left = slider:CreateTexture(nil, "ARTWORK")
left:SetAtlas("Minimal_SliderBar_Left", true)
left:SetPoint("LEFT", slider, "LEFT", -3, 0)
local right = slider:CreateTexture(nil, "ARTWORK")
right:SetAtlas("Minimal_SliderBar_Right", true)
right:SetPoint("RIGHT", slider, "RIGHT", 3, 0)
local middle = slider:CreateTexture(nil, "ARTWORK")
middle:SetAtlas("_Minimal_SliderBar_Middle", true)
middle:SetPoint("LEFT", left, "RIGHT", 0, 0)
middle:SetPoint("RIGHT", right, "LEFT", 0, 0)
local thumb = slider:CreateTexture(nil, "ARTWORK")
thumb:SetAtlas("Minimal_SliderBar_Button", true)
thumb:SetSize(16, 16)
slider:SetThumbTexture(thumb)
-- Hide template's built-in labels (they may show wrong values):
if slider.Low then slider.Low:Hide() end
if slider.High then slider.High:Hide() end
if slider.Text then slider.Text:Hide() end
```

### 4. ColorPickerFrame needs multiple callbacks
TBC may call `swatchFunc`, `func`, or `opacityFunc` on accept. Wire all three:
```lua
ColorPickerFrame.swatchFunc = function() ... end  -- primary on some versions
ColorPickerFrame.func = function() ... end        -- primary on others
ColorPickerFrame.opacityFunc = function() ... end -- if opacity changes
ColorPickerFrame.cancelFunc = function(previous)  -- previous has {r,g,b}
    if previous then revert(previous.r, previous.g, previous.b)
    else revert(origR, origG, origB) end
end
```

### 5. SavedVariables reset: use `wipe()`, not reassignment
```lua
-- BROKEN: EscapeComboPointsDB = {}  -- orphans old reference
-- FIXED: wipe(EscapeComboPointsDB)  -- clears in place
```
After wiping, call `ns:InitConfig()` to repopulate defaults. UI widgets must be rebuilt since they hold stale references.

### 6. Combo Points API (dual-compat)
```lua
local function GetComboPoints()
    local ok, points = pcall(UnitPower, "player", 4)  -- Enum.PowerType.ComboPoints
    if ok and points and points > 0 then return points end
    if GetComboPoints then
        ok, points = pcall(GetComboPoints, "player", "target")
        if ok and points and points > 0 then return points end
    end
    return 0
end
```
Events: `UNIT_COMBO_POINTS` and `UNIT_POWER_UPDATE` both fire.

### 7. Nameplate API
```lua
-- Both available in TBC Anniversary:
C_NamePlate.GetNamePlateForUnit("nameplate1")  -- returns plate frame
C_NamePlate.GetNamePlates()                     -- all active plates
-- Always guard: if C_NamePlate and C_NamePlate.GetNamePlateForUnit then
```
Hook pattern: `hooksecurefunc("CompactUnitFrame_UpdateName", callback)`
Check `frame:IsForbidden()` and `IsNameplateUnit(frame.unit)` (pattern: `^nameplate%d+$`).

### 8. Slash commands: register inside ADDON_LOADED
Register slash commands inside the `ADDON_LOADED` handler, not at file top-level:
```lua
if event == "ADDON_LOADED" and ... == ADDON_NAME then
    SLASH_ECP1 = "/ecp"
    SlashCmdList["ECP"] = function(msg) ... end
end
```

### 9. Hooking EditMacro to intercept macro generation
When another addon generates macros (e.g., RestedXP's targeting macro), hook `EditMacro` to modify the content before it's saved:
```lua
if EditMacro then
    local origEditMacro = EditMacro
    EditMacro = function(macroID, name, icon, body, ...)
        if name and body and name == "RXPtargeting" then
            local fixedBody = FixMacroContent(body)  -- your fix function
            if fixedBody ~= body then
                return origEditMacro(macroID, name, icon, fixedBody, ...)
            end
        end
        return origEditMacro(macroID, name, icon, body, ...)
    end
end
```
**Pitfall**: `EditMacro` is called frequently. Filter by macro name to avoid unnecessary processing.

### 10. AddMessage hook with recursion prevention
Hooking `DEFAULT_CHAT_FRAME.AddMessage` for logging can cause infinite recursion if your own log messages trigger the hook. Always filter:
```lua
hooksecurefunc(DEFAULT_CHAT_FRAME, "AddMessage", function(self, msg, ...)
    if msg and type(msg) == "string" then
        -- CRITICAL: filter out your own messages
        if msg:find("MyAddonName") then return end
        if msg:find("MY_LOG_PREFIX") then return end
        
        if msg:find("TargetAddon") then
            LogEntry("CATEGORY", msg:sub(1, 200))  -- truncate long messages
        end
    end
end)
```
**Without the filter, the log fills with thousands of recursive entries per second.**

### 11. CancelUnitBuff takes INDEX, not NAME
`CancelUnitBuff("player", buffName)` silently fails or errors. The second argument must be the buff's **numeric index** (1-40). To cancel a buff by name, iterate first:
```lua
for i = 1, 40 do
    local name = UnitBuff("player", i)
    if not name then break end
    if name == targetName then
        pcall(CancelUnitBuff, "player", i)  -- index
        break
    end
end
```
Fallback chain: `CancelPlayerBuff(index)` → `RunMacroText("/cancelaura <name>")`. Always `pcall()`.

### 12. Protected functions cannot be called from addon code
`InteractUnit("target")`, `TargetUnit("target")` etc. are protected. `SecureActionButton:Click()` from Lua does NOT provide the hardware-input context these functions require. Do NOT attempt to programmatically trigger NPC interactions. Workaround: cancel the blocking condition (form, debuff), then tell the user to click the NPC again.

## TOC File
```
## Interface: 20505
## Title: AddonName
## Notes: Description
## Author: Name
## Version: 1.0
## SavedVariables: AddonNameDB

Core.lua
Config.lua
```

## Config Panel Architecture
- Extract content building into a separate `BuildContent()` function
- Store panel/scrollFrame/scrollBar references on `ns` for rebuild access
- Use `contentCounter` to generate unique frame names on rebuild
- Reset: `wipe(DB)` → `InitConfig()` → destroy old content → `BuildContent()` fresh
- Use ScrollFrame with UIPanelScrollBarTemplate for long option lists

## Safe Patterns
- Use `pcall()` for API calls that differ between versions
- Always check `frame:IsForbidden()` before accessing nameplate children
- Guard `C_NamePlate` with existence check
- Use `strfind(unit, "^nameplate%d+$")` to identify nameplate units
- Frame strata: `"HIGH"` for overlay UI on nameplates

## ⚠️ Protected API — Silent Failures (CRITICAL)

Many WoW functions are PROTECTED and require a hardware event. Calling from addon code silently succeeds (no error) but does nothing:

**Protected**: `CancelShapeshiftForm()`, `CancelUnitBuff()`, `RunMacroText()` (since 2.0.1), `CastSpellByName()`, `InteractUnit()`, `TargetUnit()`

**Solution**: Use `SecureActionButtonTemplate` with native action types + `SetOverrideBindingClick` for keybind:

```lua
local btn = CreateFrame("Button", nil, UIParent, "SecureActionButtonTemplate")
btn:SetAttribute("type", "cancelaura")  -- native type, NOT "macro"
btn:SetAttribute("unit", "player")
btn:SetAttribute("spell", localizedBuffName)  -- from UnitBuff()
SetOverrideBindingClick(btn, false, "F12", btn:GetName())
```

**Pitfall**: `pcall()` returns `true` for protected calls that silently fail — don't trust pcall as a success indicator for protected functions.
**Pitfall**: `CancelUnitBuff(unit, index)` takes buff INDEX (number), not name.
**Pitfall**: `/cancelform` and `/cancelaura` are secure macro commands — only work in secure context (player click on SecureActionButton).
**Pitfall**: `InsecureActionButtonTemplate` + macros still blocks protected commands when called from addon code. Only player hardware clicks work.

## NPC Name Resolution via GameTooltip
Get any NPC's localized name by ID without targeting them:

**Note**: Zygor Guides Viewer uses the same trick via `Localizers:GetTranslatedNPC(id)` in `Localizers.lua`. RestedXP uses `addon.GetNpcName(id)`. This is the standard pattern across WoW guide addons.
```lua
local tooltip = CreateFrame("GameTooltip", "MyTooltip", nil, "GameTooltipTemplate")
tooltip:SetOwner(WorldFrame, "ANCHOR_BOTTOMRIGHT")
tooltip:ClearLines()
tooltip:SetHyperlink(string.format("unit:Creature-0-0-0-0-%d", npcID))
if tooltip:IsShown() then
    local name = _G["MyTooltipTextLeft1"]:GetText()
    name = name:match("^|c%x%x%x%x%x%x%x%x(.*)|r$") or name
    -- name is the localized NPC name
end
tooltip:Hide()
```
**This is the standard trick** used by RestedXP, Questie, and other addons. Works in Classic/TBC/WotLK.
Cache results — don't call per-frame. Rate limit to ~1 query per 1.5 seconds.

## Hooking Other Addons
Pattern for hooking into another addon's functions:
```lua
-- After the target addon loads (check with ADDON_LOADED or just try)
local targetAddon = _G.RXPGuides  -- or _G.WhateverAddon
if targetAddon then
    hooksecurefunc(targetAddon, "FunctionName", function(self, ...)
        -- Your code runs AFTER the original function
        -- self is the addon table, ... are the arguments
    end)
end
```
**Pitfalls:**
- `hooksecurefunc` runs AFTER the original, can't prevent execution
- The hooked function's `self` depends on how it was called (addon.method vs addon:method)
- Some addon functions are `local` and can't be hooked — look for the global reference
- Use `C_Timer.After(0.1, callback)` to run after the addon finishes its update cycle

## Interface Version Numbers
- Classic Era: `11505`
- Anniversary (Season of Discovery / Classic 20th): `11508`
- TBC Classic: `20505`
- WotLK Classic: `30403`
- Retail: `110002`+
- Use comma-separated list in TOC for multi-version: `## Interface: 11508, 110205, 20505`
