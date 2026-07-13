# TBC Classic Anniversary API Notes

## Interface Version
- **TBC Classic Anniversary**: `20505` (also supports 20506)
- Addons path: `C:\Program Files (x86)\World of Warcraft\_anniversary_\Interface\AddOns\`

## Combo Points API
TBC 2.5.5 may support both old and new APIs — try in order:
1. `UnitPower("player", 4)` — modern API, Enum.PowerType.ComboPoints = 4
2. `GetComboPoints("player", "target")` — classic API, may not exist
3. `GetComboPoints("vehicle", "target")` — vehicle variant

**Always wrap in pcall()**: The API availability depends on the exact build.

## Nameplate System
- Uses modern CompactUnitFrame system (same as Retail)
- `C_NamePlate.GetNamePlateForUnit(unit)` exists but verify with nil check
- `hooksecurefunc("CompactUnitFrame_UpdateName", ...)` is the standard hook point
- Unit tokens: `nameplate1` through `nameplate40`
- `NAME_PLATE_UNIT_ADDED` / `NAME_PLATE_UNIT_REMOVED` events fire correctly
- Nameplates use `UnitFrame.healthBar` sub-frame (not direct `healthBar`)

## ColorPickerFrame (Classic)
Use direct property assignment, NOT `SetupColorPickerAndShow`:
```lua
ColorPickerFrame:SetColorRGB(r, g, b)
ColorPickerFrame.hasOpacity = false
ColorPickerFrame.func = function() ... end        -- called on OK
ColorPickerFrame.cancelFunc = function() ... end   -- called on Cancel
ColorPickerFrame:Show()
```

## Textures Available in TBC
These built-in textures work without external files:
- `Interface\\Minimap\\UI-Minimap-Background` — solid circle, good for orbs
- `Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight` — glossy highlight
- `Interface\\Tooltips\\UI-Tooltip-Border` — metallic border (SetBackdrop edgeFile)
- `Interface\\GossipFrame\\HealerGossipIcon` — circular icon, good for glow effects
- `Interface\\TargetingFrame\\UI-TargetingFrame-BarFill` — generic bar fill

## Existing Addon Analysis Results (User's Setup)
User has these addons installed (useful for API version and pattern reference):
- **KNameplateColor** — nameplate coloring via `hooksecurefunc("CompactUnitFrame_UpdateName")`
- **RougeUI** — extensive UI modification, uses `hooksecurefunc` for dozens of functions
- **EasyTarget** — simple targeting addon, single-file, SecureActionButton
- **EnemyCompass** — range-based compass, uses LibRangeCheck-3.0
- **RXPGuides** — leveling guides, multi-file with localization
- **Questie** — quest helper, large addon with libs
- **Leatrix_Plus** — UI tweaks, confirms Interface 20505

## ⚠️ BROKEN APIs in TBC Anniversary 2.5.5

### Config Panel Registration
- **`InterfaceOptions_AddCategory()`** — SILENTLY IGNORES registrations. Panel never appears.
- **FIX**: Use `Settings.RegisterCanvasLayoutCategory(frame, name)` + `Settings.RegisterAddOnCategory(category)`
- **Opening**: Use `Settings.OpenToCategory(categoryID)` (no double-call needed)
- **Fallback**: `InterfaceOptions_AddCategory` still works in Classic Era

### Slider Controls
- **`OptionsSliderTemplate`** — renders without visible track/bar. Handle floats with no rail.
- **FIX**: Use `MinimalSliderTemplate` + atlas textures: `Minimal_SliderBar_Left`, `_Minimal_SliderBar_Middle`, `Minimal_SliderBar_Right`, `Minimal_SliderBar_Button`
- **Reference**: Leatrix Plus uses this exact approach in its `LeaPlusConfigurationPanelSliderTemplate`

### Slash Commands
- Register **inside `ADDON_LOADED` handler**, not at file top level. May not be processed if registered too early.

## Common WoW API (TBC 2.5.5)
- `UnitExists(unit)`, `UnitIsUnit(unit1, unit2)`, `UnitIsDead(unit)`
- `UnitIsFriend(unit, "player")`, `UnitIsPlayer(unit)`
- `UnitClass(unit)`, `UnitLevel(unit)`, `UnitName(unit)`
- `CreateFrame("Frame", name, parent, template)`
- `frame:SetBackdrop({})`, `frame:SetBackdropBorderColor()`
- `frame:SetFrameStrata("HIGH")`, `frame:SetClampedToScreen(true)`
- `hooksecurefunc("BlizzardFunc", postHook)`
- `Settings.RegisterCanvasLayoutCategory(frame, name)` — config panel (TBC Anniversary)
- `Settings.RegisterAddOnCategory(category)` — register panel
- `Settings.OpenToCategory(categoryID)` — open panel
