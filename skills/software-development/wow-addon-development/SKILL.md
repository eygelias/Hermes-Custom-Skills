---
name: wow-addon-development
description: Create WoW addons for Classic/TBC/WotLK — TOC structure, SavedVariables, API compatibility, nameplate/UI hooking, config panels, security (no taint).
tags: [wow, addon, lua, world-of-warcraft, classic, tbc, nameplates, ui]
triggers:
  - wow addon
  - create addon
  - wow classic addon
  - tbc addon
  - nameplate addon
  - combo points
  - blizzard ui
  - wow lua
  - wow interface
---

# WoW Addon Development

Create addons for World of Warcraft Classic/TBC/WotLK. Covers structure, API compatibility, UI hooking, config panels, and security.

## Prerequisites — ALWAYS DO FIRST

Before writing any addon code:

1. **Read the user's existing addons** to determine:
   - `## Interface:` version number (e.g. 20505 for TBC Classic Anniversary)
   - Coding style (single file vs multi-file, comments language)
   - Libraries used (LibStub, Ace3, etc.)
   - How they handle SavedVariables
2. **Check relevant addons** that do similar things (nameplate mods, unit frame addons) for hook patterns
3. Ask the user which WoW version/expansion if not clear

## Addon File Structure

```
MyAddon/
├── MyAddon.toc           -- Manifest (required)
├── Core.lua              -- Main logic
├── Config.lua            -- Options panel (optional)
├── libs/                 -- Third-party libraries (optional)
│   └── LibStub/
└── media/                -- Textures, sounds (optional)
```

### TOC File Format

```
## Interface: 20505
## Title: MyAddon
## Notes: Description shown in addon list
## Author: AuthorName
## Version: 1.0
## SavedVariables: MyAddonDB
## OptionalDeps: LibStub, Ace3

libs\LibStub\LibStub.lua
Core.lua
Config.lua
```

**Interface versions** (as of 2026):
- Classic Era: 11505
- TBC Classic Anniversary: 20505 (also 20506)
- WotLK Classic: 30405
- Cata Classic: 40405
- Retail: 110200

## Core Addon Pattern

```lua
local ADDON_NAME, ns = ...

-- Default config
local DEFAULTS = {
    enabled = true,
    scale = 1.0,
}

-- Bootstrap
local boot = CreateFrame("Frame")
boot:RegisterEvent("ADDON_LOADED")
boot:SetScript("OnEvent", function(self, event, addon)
    if addon ~= ADDON_NAME then return end
    self:UnregisterEvent("ADDON_LOADED")
    
    -- Init SavedVariables
    MyAddonDB = MyAddonDB or {}
    ns.db = MyAddonDB
    for k, v in pairs(DEFAULTS) do
        if ns.db[k] == nil then ns.db[k] = v end
    end
    
    -- Register events
    ns.eventFrame = CreateFrame("Frame")
    ns.eventFrame:SetScript("OnEvent", function(_, e, ...)
        if ns[e] then ns[e](ns, ...) end
    end)
    ns.eventFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
    -- ... more events
    
    -- Slash commands
    SLASH_MYADDON1 = "/myaddon"
    SlashCmdList["MYADDON"] = function(msg) ... end
    
    print("|cFF00FF00[MyAddon]|r Loaded.")
end)
```

## Nameplate Hooking

### Key Events
- `NAME_PLATE_UNIT_ADDED(unit)` — nameplate appeared
- `NAME_PLATE_UNIT_REMOVED(unit)` — nameplate gone
- `PLAYER_TARGET_CHANGED` — target changed

### Key API
```lua
-- Get nameplate frame for unit token
local plate = C_NamePlate.GetNamePlateForUnit(unit)

-- Hook into Blizzard's nameplate update (post-hook, safe)
hooksecurefunc("CompactUnitFrame_UpdateName", function(frame)
    if frame:IsForbidden() then return end
    if not frame.unit or not strfind(frame.unit, "^nameplate%d+$") then return end
    -- Your logic here
end)
```

### Display Pool Pattern
Use a pool of reusable frames instead of creating/destroying:
```lua
ns.pool = {}
ns.activeDisplays = {}

function ns:GetOrCreateDisplay()
    if #self.pool > 0 then
        local d = table.remove(self.pool)
        d.frame:Show()
        return d
    end
    -- Create new...
end

function ns:ReturnDisplay(display)
    display.frame:Hide()
    table.insert(self.pool, display)
end
```

### Visibility
- Nameplate child frames auto-hide when parent hides (Shift+V toggle)
- No need to manually track nameplate visibility
- Set `frame:SetParent(nameplate)` so it follows the plate

## Config Panel (Blizzard Interface Options)

### ⚠️ CRITICAL: InterfaceOptions_AddCategory is BROKEN in TBC Anniversary 2.5.5

`InterfaceOptions_AddCategory()` **silently ignores registrations** in TBC Anniversary 2.5.5. The panel never appears. Use the **Settings API** with fallback:

```lua
function ns:SetupConfig()
    local panel = CreateFrame("Frame", ADDON_NAME .. "Config", UIParent)
    panel.name = "MyAddon"
    
    -- Widgets: sliders, checkboxes, dropdowns, color buttons
    -- ...
    
    -- Register with compatible API
    if Settings and Settings.RegisterCanvasLayoutCategory then
        -- TBC Anniversary 2.5.5 / Retail 10.0+
        local category = Settings.RegisterCanvasLayoutCategory(panel, panel.name)
        category.ID = panel.name
        Settings.RegisterAddOnCategory(category)
        ns.optionsCategory = category
    else
        -- Classic Era / older versions
        InterfaceOptions_AddCategory(panel)
    end
    ns.optionsPanel = panel
end

-- Open panel (must handle both APIs):
if Settings and Settings.OpenToCategory and ns.optionsCategory then
    Settings.OpenToCategory(ns.optionsCategory:GetID())
elseif ns.optionsPanel then
    InterfaceOptionsFrame_OpenToCategory(ns.optionsPanel)
    InterfaceOptionsFrame_OpenToCategory(ns.optionsPanel)  -- double-call bug
end
```

### Sliders — MinimalSliderTemplate (NOT OptionsSliderTemplate)

**`OptionsSliderTemplate` does NOT render the track/bar** in TBC Anniversary. Use `MinimalSliderTemplate` with atlas textures (same approach as Leatrix Plus):

```lua
local slider = CreateFrame("Slider", name, parent, "MinimalSliderTemplate")
slider:SetWidth(180)
slider:SetHeight(18)
slider:SetMinMaxValues(lo, hi)
slider:SetValueStep(step)
slider:SetObeyStepOnDrag(true)

-- Track (visible bar) using atlas textures
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

-- Thumb (draggable button)
local thumb = slider:CreateTexture(nil, "ARTWORK")
thumb:SetAtlas("Minimal_SliderBar_Button", true)
thumb:SetSize(16, 16)
slider:SetThumbTexture(thumb)

-- Enable mousewheel
slider:EnableMouseWheel(true)
slider:SetScript("OnMouseWheel", function(self, delta)
    local v = self:GetValue() + (step * delta)
    self:SetValue(math.max(lo, math.min(hi, v)))
end)
```

### ScrollFrame for Overflow Prevention

Config panels with many options need a ScrollFrame to prevent content from overflowing:

```lua
local scrollFrame = CreateFrame("ScrollFrame", nil, panel)
scrollFrame:SetPoint("TOPLEFT", panel, "TOPLEFT", 0, -8)
scrollFrame:SetPoint("BOTTOMRIGHT", panel, "BOTTOMRIGHT", -26, 8)

local scrollBar = CreateFrame("Slider", nil, scrollFrame, "UIPanelScrollBarTemplate")
scrollBar:SetPoint("TOPLEFT", scrollFrame, "TOPRIGHT", 4, -16)
scrollBar:SetPoint("BOTTOMLEFT", scrollFrame, "BOTTOMRIGHT", 4, 16)
scrollBar:SetWidth(16)

local content = CreateFrame("Frame", nil, scrollFrame)
content:SetWidth(450)
scrollFrame:SetScrollChild(content)
-- Build all widgets on content, then: content:SetHeight(totalHeight)
```

### Slash Command Registration Timing
Register slash commands **inside the `ADDON_LOADED` handler**, not at file load time. TBC Anniversary may not process them if registered too early:

```lua
-- Inside ADDON_LOADED handler, AFTER initializing SavedVariables:
SLASH_MYADDON1 = "/myaddon"
SLASH_MYADDON2 = "/ma"
SlashCmdList["MYADDON"] = function(msg)
    msg = strlower(strtrim(msg or ""))
    if msg == "config" then ...
end
```

## Protected API Functions (WoW Security Model)

**CRITICAL**: Many WoW API functions are PROTECTED and require a hardware event (real player click/keypress). Calling them from addon code silently fails — `pcall()` returns `true` (no error thrown) but the action never executes. This is the #1 source of "my addon calls X but nothing happens" bugs.

### Protected Functions (require hardware event)
- `CancelShapeshiftForm()` — silently does nothing from addon code
- `CancelUnitBuff(unit, index)` — silently does nothing
- `CancelPlayerBuff(index)` — silently does nothing
- `RunMacroText(text)` — PROTECTED since patch 2.0.1. If text contains secure commands (`/cast`, `/cancelaura`, `/cancelform`), they are silently blocked
- `CastSpellByName()`, `UseItemByName()` — all protected
- `TargetUnit()`, `FocusUnit()` — protected
- `InteractUnit()` — protected

### How to Execute Protected Actions
The ONLY way is through a **SecureActionButtonTemplate** triggered by a real player input:
1. Create button with `SecureActionButtonTemplate`
2. Set action attributes (`type`, `spell`, `unit`, etc.)
3. Player must physically click the button OR press a key bound via `SetOverrideBindingClick`

```lua
-- Example: Cancel a specific buff (works for any localized name)
local btn = CreateFrame("Button", "MyCancelBtn", UIParent, "SecureActionButtonTemplate")
btn:RegisterForClicks("AnyUp")
btn:SetAttribute("type", "cancelaura")  -- native action type, NOT macro
btn:SetAttribute("unit", "player")
btn:SetAttribute("spell", buffName)     -- localized name from UnitBuff()

-- Bind to a key (F12 in this case)
SetOverrideBindingClick(btn, false, "F12", btn:GetName())
-- Player presses F12 → secure environment cancels the buff
```

### SecureActionButton Action Types
| Type | Attributes | Behavior |
|------|-----------|----------|
| `"spell"` | `unit`, `spell` | Casts spell by name |
| `"item"` | `unit`, `item` | Uses item |
| `"macro"` | `macrotext` | Runs macro (secure commands inside still need hardware) |
| `"cancelaura"` | `unit`, `spell` | **Cancels buff by name** — native, no macro needed |
| `"target"` | `unit` | Changes target |
| `"click"` | `clickbutton` | Clicks another button |

### Druid Form Cancellation Pattern
```lua
-- Get localized form name (works in ANY language)
local function GetFormBuffName()
    for i = 1, 40 do
        local name = UnitBuff("player", i)
        if not name then break end
        if DRUID_FORMS[name] then return name end
    end
    return nil
end

-- Secure button with "cancelaura" native type
local cancelBtn = CreateFrame("Button", nil, UIParent, "SecureActionButtonTemplate")
cancelBtn:SetAttribute("type", "cancelaura")
cancelBtn:SetAttribute("unit", "player")
-- Update spell attribute with localized name before binding
cancelBtn:SetAttribute("spell", GetFormBuffName())
SetOverrideBindingClick(cancelBtn, false, "F12", cancelBtn:GetName())
```

**Pitfall**: `/cancelform` and `/cancelaura` in macros are SECURE COMMANDS. They work only when the macro runs in a secure context (player click on SecureActionButton). `RunMacroText("/cancelform")` from addon code does NOT work.

**Pitfall**: `CancelUnitBuff("player", buffName)` — second arg must be the buff INDEX (number), not the name. Use `UnitBuff("player", i)` to find the index first.

**Pitfall**: `InsecureActionButtonTemplate` (patch 7.2.0+) can hold macro attributes but protected commands inside the macro are STILL blocked when called from addon code. Only `SecureActionButtonTemplate` + real hardware event works.

### Leatrix_Plus Reference
Leatrix_Plus uses `InsecureActionButtonTemplate` + `/cancelform` on the TaxiFrame — but this button is VISIBLE and the PLAYER clicks it. It does NOT auto-cancel. This confirms that form cancellation requires player interaction in WoW.

## Localization / Translation of Existing Addons

When translating an installed WoW addon, preserve syntax and addon-internal identifiers first; visible localized text second.

1. **Back up every related addon folder before editing** (especially LoadOnDemand companion folders like `ItemRack` + `ItemRackOptions`). Put backup outside `Interface/AddOns`, e.g. Desktop timestamp folder.
2. **Translate only user-visible strings**: TOC `## Notes`, button labels, tooltips, popups, slash-help text, readme/changelog. Avoid broad blind replacement in code.
3. **Do not translate internal tokens** unless every code path is deliberately migrated:
   - XML/frame suffixes and globals: `Enabled`, `Text`, `Name`, `Icon`, `Button`, `$parentEnabled`, etc.
   - Event type enum values used in logic/SavedVariables: `Buff`, `Stance`, `Zone`, `Specialization`, `Script`.
   - Default event keys if used as lookup keys: `Primary Spec`, `Secondary Spec`, `~CombatQueue`, `~Unequip`.
   - Slash command tokens, patterns, item links, texture paths, binding names (`CLICK ItemRackButton0:LeftButton`).
4. **Good pattern**: exact string map + string-literal replacement for Lua, exact `text="..."` attribute replacement for XML. This avoids changing identifiers and code symbols.
5. **Watch for translated XML text breaking Lua lookups**: if Lua does `_G[frame:GetName().."Enabled"]`, do not change XML child name suffix to localized text. If a dropdown displays localized labels but code compares English enum strings, either keep displayed labels English or add a separate localization map; shortest safe fix is keep enum display tokens unchanged.
6. **Verify before final**:
   - Parse XML files with Python `xml.etree.ElementTree.parse`.
   - Run a lightweight Lua lexer/string-balance check if `lua`/`luac` is unavailable.
   - Assert key internal tokens still exist (`eventType=="Buff"`, `event.Type=="Zone"`, binding action names, etc.).

## Pitfalls

### 🔴 CRITICAL (will silently fail or crash in TBC Anniversary 2.5.5/2.5.6)

1. **`InterfaceOptions_AddCategory` is BROKEN** — silently ignores registrations. Use `Settings.RegisterCanvasLayoutCategory` + `Settings.RegisterAddOnCategory` instead. See Config Panel section above.
2. **`OptionsSliderTemplate` renders without visible track** — use `MinimalSliderTemplate` with atlas textures instead. See Sliders section above.
3. **Slash commands at file load time** — register inside `ADDON_LOADED` handler.
4. **Some legacy globals moved under `C_AddOns`** — use fallbacks:
   ```lua
   local LoadAddonCompat = LoadAddOn or (C_AddOns and C_AddOns.LoadAddOn)
   local GetMetadataCompat = GetAddOnMetadata or (C_AddOns and C_AddOns.GetAddOnMetadata)
   ```
5. **`OptionsCheckButtonTemplate` may be missing** — use `InterfaceOptionsCheckButtonTemplate` for config checkboxes.
6. **`CombatText_AddMessage` may be missing** — do NOT fall back to `CombatText:AddMessage` in TBC Anniversary 2.5.6; its implementation passes incompatible color tables into `FontString:SetTextColor` and crashes. Use `UIErrorsFrame:AddMessage` or `ChatFrame1:AddMessage` instead:
   ```lua
   local function AddCombatText(message, scrollFunction, r, g, b)
       r, g, b = r or 1, g or 1, b or 1
       if CombatText_AddMessage then
           CombatText_AddMessage(message, scrollFunction or CombatText_StandardScroll, r, g, b)
       elseif UIErrorsFrame and UIErrorsFrame.AddMessage then
           UIErrorsFrame:AddMessage(message, r, g, b, 1)
       elseif ChatFrame1 then
           ChatFrame1:AddMessage(message, r, g, b)
       end
   end
   ```
7. **`InterfaceOptions_AddCategory` may be nil** — for older addons that call it directly, add a small compatibility wrapper and replace calls:
   ```lua
   local function AddOptionsCategory(panel)
       if Settings and Settings.RegisterCanvasLayoutCategory then
           if panel.parent and Settings.RegisterCanvasLayoutSubcategory and Settings.GetCategory then
               local parent = Settings.GetCategory(panel.parent)
               if parent then
                   Settings.RegisterCanvasLayoutSubcategory(parent, panel, panel.name)
                   return
               end
           end
           local category = Settings.RegisterCanvasLayoutCategory(panel, panel.name)
           category.ID = panel.name
           Settings.RegisterAddOnCategory(category)
       elseif InterfaceOptions_AddCategory then
           InterfaceOptions_AddCategory(panel)
       end
   end
   ```

### TBC Classic API Compatibility
- **GetComboPoints** may not exist — wrap in `pcall()` or check `type(GetComboPoints) == "function"` first
- **UnitPower("player", 4)** is the modern API for combo points — try this first
- **C_NamePlate.GetNamePlateForUnit** — check existence before calling; fallback to iterating WorldFrame children
- Always use `pcall()` for API calls that differ between expansions

### 🔴 CancelUnitBuff Takes INDEX, Not NAME
`CancelUnitBuff("player", buffName)` is WRONG — the second argument must be the **buff index** (1-40), not the buff name. To cancel a specific buff by name, iterate first:
```lua
for i = 1, 40 do
    local name = UnitBuff("player", i)
    if not name then break end
    if name == targetBuffName then
        CancelUnitBuff("player", i)  -- index, not name
        break
    end
end
```
Also try `CancelPlayerBuff(index)` as fallback (Classic API). Always wrap in `pcall()`.
As a last resort, `RunMacroText("/cancelaura <name>")` works because the macro parser handles name lookup internally.

### Protected Functions Cannot Be Called From Addon Code
`InteractUnit("target")`, `TargetUnit("target")`, and other protected functions throw "function is protected" even when called via `SecureActionButton:Click()`. The `:Click()` from Lua does NOT provide the hardware input context that protected functions require. Do NOT attempt to programmatically trigger NPC interactions from addon code.
**Workaround**: Cancel the form/debuff, then inform the user to click the NPC again. Or use `RunMacroText("/targetexact Name")` followed by `/interact` (if available) — but even this may fail for `InteractUnit`.

### NPC Interaction Events
These events fire when the player successfully opens an NPC interaction UI (some only work out of shapeshift form):
- `GOSSIP_SHOW` — general NPC dialog (flight masters, quest givers with gossip)
- `MERCHANT_SHOW` — vendor windows
- `TAXIMAP_OPENED` — flight master map
- `TRAINER_SHOW` — class/profession trainers
- `BANKFRAME_OPENED` — bank
- `QUEST_GREETING` — quest list from NPC
- `QUEST_DETAIL` / `QUEST_PROGRESS` / `QUEST_COMPLETE` — individual quest frames
- `PETITION_SHOW` — guild petitions

Use `UnitName("npc")` to get the NPC name. Use `C_GossipInfo.GetOptions()` + `C_GossipInfo.SelectOption(optionID)` to programmatically select gossip options (in TBC Anniversary, `optionID` is the 1-based index, not a real ID).

### Druid Shapeshift Detection
`GetShapeshiftForm()` returns 0 (human) or 1+ (shapeshifted). This is the primary check. As backup, scan buffs with `UnitBuff("player", i)` and match against localized form names (e.g. "Cat Form" / "Forma de felino"). Always include both English and the client's locale.

### Gossip Frame Button Clicking
To programmatically click a gossip option when `C_GossipInfo.SelectOption` isn't available:
```lua
for i = 1, 20 do
    local btn = _G["GossipTitleButton" .. i]
    if btn and btn:IsVisible() and btn:IsEnabled() then
        btn:Click()
        break
    end
end
```

### ColorPickerFrame (Classic vs Retail)
**Classic/TBC** — direct property assignment:
```lua
ColorPickerFrame:SetColorRGB(r, g, b)
ColorPickerFrame.hasOpacity = false
ColorPickerFrame.func = function()
    local r, g, b = ColorPickerFrame:GetColorRGB()
    -- apply color
end
ColorPickerFrame.cancelFunc = function()
    -- revert to original
end
ColorPickerFrame:Show()
```

**Retail** — use the newer API (if it exists):
```lua
if ColorPickerFrame.SetupColorPickerAndShow then
    ColorPickerFrame:SetupColorPickerAndShow({...})
end
```

### Lua Backslash Escaping in write_file Tool
When writing Lua files through the `write_file` tool, backslashes in texture paths go through JSON → Python → file. The correct approach:
- Write `"Interface\\Minimap\\UI-Minimap-Background"` (double backslash in source)
- At runtime, Lua interprets `\\` as a single `\`
- **Pitfall**: The write_file tool may add extra escaping layers — always verify the file content with read_file or grep after writing

### Frame Initialization Race Guards
Some older Ace3/TBC addons can fire `OnShow`, `ZoneChanged`, or resize handlers before custom frame bookkeeping tables finish initializing. Example symptoms:
- `SetWindowTop()` crashes because `window.Below` is nil.
- `RestoreMainWindowPosition()` crashes because `Frame.Rows` is nil.

Minimal durable fix: guard shared functions, not every caller:
```lua
function Addon:SetWindowTop(window)
    if InCombatLockdown() then return end
    if not window then return end
    if not TopWindow then TopWindow = UIParent end
    if not window.Below then
        Addon:AddWindow(window)
        return
    end
    if TopWindow == window then return end
    -- existing ordering code...
end

function Addon:RestoreMainWindowPosition(x, y, width, height)
    x = x or db.profile.MainWindow.Position.x or 211
    y = y or db.profile.MainWindow.Position.y or 54
    width = width or db.profile.MainWindow.Position.w or 200
    height = height or db.profile.MainWindow.Position.h or 34
    if Frame.Rows then
        for _, row in pairs(Frame.Rows) do row:SetWidth(width - 4) end
    end
end
```

### Frame Security (Taint)
- **Safe**: Creating visual frames, textures, fontstrings
- **Safe**: hooksecurefunc (post-hooks don't taint)
- **Unsafe**: Modifying protected frames (action buttons, unit frames during combat)
- **Unsafe**: Calling protected functions from insecure code
- **Safe**: SetParent() on your own frames to nameplates
- **Check**: `frame:IsForbidden()` before accessing frame properties

### Slash Command Registration
```lua
SLASH_MYADDON1 = "/myaddon"
SLASH_MYADDON2 = "/ma"  -- optional short alias
SlashCmdList["MYADDON"] = function(msg)
    msg = strlower(strtrim(msg or ""))
    if msg == "config" then ...
end
```

### Double-call Bug
`InterfaceOptionsFrame_OpenToCategory` must be called twice to actually show the panel. Always use:
```lua
InterfaceOptionsFrame_OpenToCategory(panel)
InterfaceOptionsFrame_OpenToCategory(panel)
```
This applies to the legacy API only. `Settings.OpenToCategory` does NOT need double-call.

## Support Files
- `references/tbc-api-notes.md` — TBC Classic API details, texture paths, existing addon analysis
- `references/buff-aura-npc-api.md` — Buff/aura cancellation (CancelUnitBuff pitfall), druid form detection, NPC interaction events, gossip API, protected function limitations
- `references/tbc-anniversary-legacy-addon-compat.md` — Compatibility shims for legacy addons on TBC Anniversary 2.5.6 (Settings API, templates, combat text, moved globals)
- `templates/tbc-addon.toc` — Copy-paste TOC template for TBC Classic (Interface 20505)
