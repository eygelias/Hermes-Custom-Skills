# NPC Name Source Reliability — TBC Anniversary

Use when translated NPC names in RXP guides do not match the live WoW client.

## Observed source quality

1. **Live WoW client via `UnitName(unit)` / GameTooltip** — strongest source for what target macros must use.
   - Only trust uncontrolled NPC units.
   - Do **not** cache `UnitPlayerControlled(unit)` units; hunter pets/demon pets reuse creature IDs but show custom names and corrupt the cache.
   - Example corruption seen: `416 Imp => Jaktog`, `417 Felhunter => Bruughon`.
2. **Wowhead TBC Classic localized pages** — best external fallback by NPC ID.
   - URL pattern: `https://www.wowhead.com/tbc/es/npc=<id>`
   - Page title/H1 gives localized name; page includes `Inglés: <English Name>` for verification.
   - Verified examples:
     - `7856 Southsea Freebooter => Filibustero de los Mares del Sur`
     - `113 Stonetusk Boar => Jabalí colmillopétreo`
     - `2185 Darkshore Thresher => Trillador de la Costa Oscura`
3. **`questiedb_es.json`** — best local static source currently available. Has IDs + English + locale names.
4. **RXPGuides `NPCnames.lua` / `npcnames_esES.json`** — useful but incomplete.
5. **CMaNGOS merged locale data** — broad, but ID/name connection can be weaker for RXP guide text; use below client/Wowhead/QuestieDB for NPC macro correctness.

## Recommended priority

```text
manual/client verified > Wowhead TBC ES by NPC ID > questiedb_es.json > RXPGuides NPCnames > CMaNGOS > leave English + log unresolved
```

## Runtime cache guard

In `RXPNameFixer.lua`, guard captures:

```lua
local function CaptureUnit(unit)
    if not unit or not UnitExists(unit) or UnitIsPlayer(unit) then return end
    -- ponytail: cache solo NPCs reales; pets/demonios con nombre personalizado contaminan IDs globales.
    if UnitPlayerControlled and UnitPlayerControlled(unit) then return end
    local guid = UnitGUID(unit)
    local npcID = GetNpcIDFromGUID(guid)
    local name = UnitName(unit)
    -- cache only after this point
end
```

## Export path fix

SavedVariables live under account subfolders, not directly under `WTF/Account/SavedVariables`:

```python
account_dir = wow_base / variant / "WTF" / "Account"
for candidate in account_dir.glob("*/SavedVariables/RXPNameFixer.lua"):
    sv_path = candidate
    break
```

## Cleanup workflow after cache contamination

1. Patch `RXPNameFixer.lua` with `UnitPlayerControlled` guard.
2. Copy addon into WoW AddOns folder.
3. In game run:
   ```text
   /rxpnf clear
   /reload
   ```
4. Play with nameplates enabled to collect clean NPCs.
5. Export `RXPNameFixer.lua` SavedVariables to JSON.
6. Use exported names only as client-verified overrides, not as broad auto-replacements if cache was collected before guard existed.
