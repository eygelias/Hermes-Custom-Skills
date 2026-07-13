# TBC Anniversary 2.5.6 legacy addon compatibility notes

Use this when patching older Classic-era addons that throw nil/global/template errors after loading in TBC Anniversary.

## Patterns found useful

### Missing addon metadata/global loader
Some older globals moved or may be absent. Use local fallbacks:

```lua
local LoadAddonCompat = LoadAddOn or (C_AddOns and C_AddOns.LoadAddOn)
local GetMetadataCompat = GetAddOnMetadata or (C_AddOns and C_AddOns.GetAddOnMetadata)
```

### Options registration
`InterfaceOptions_AddCategory` can be nil. Wrap category registration:

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

### Checkbox template rename
If `CreateFrame(..., "OptionsCheckButtonTemplate")` fails, use:

```lua
"InterfaceOptionsCheckButtonTemplate"
```

### Combat text output
`CombatText_AddMessage` may be nil. `CombatText:AddMessage` signature differs from old helper: pass `(message, scrollFunction, colorObject)`.

```lua
local function AddCombatText(message, scrollFunction, r, g, b)
    r, g, b = r or 1, g or 1, b or 1
    if CombatText_AddMessage then
        CombatText_AddMessage(message, scrollFunction or CombatText_StandardScroll, r, g, b)
    elseif CombatText and CombatText.AddMessage and CreateColor then
        CombatText:AddMessage(message, scrollFunction or CombatText_StandardScroll, CreateColor(r, g, b))
    elseif UIErrorsFrame and UIErrorsFrame.AddMessage then
        UIErrorsFrame:AddMessage(message, r, g, b, 1)
    elseif ChatFrame1 then
        ChatFrame1:AddMessage(message, r, g, b)
    end
end
```

### Frame init races
Legacy addons can fire `OnShow`, zone change, or resize callbacks before custom tables exist. Prefer guarding shared functions once (`SetWindowTop`, `RestorePosition`, `ManageBarsDisplayed`, `SetBar`) instead of sprinkling caller guards.

### Verification
If no Lua interpreter exists, still verify by:
- reading patched lines back,
- checking XML with `xml.etree.ElementTree` when XML changed,
- running a lightweight `function`/`end` token count sanity check,
- asking user for fresh errors only after `/reload`.
