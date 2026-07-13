# Hermes Desktop App — Zoom Persistence

## How It Works (Source: `apps/desktop/electron/main.cjs`)

The app **already has zoom persistence built in**. No config changes needed.

### Storage mechanism
- **localStorage key:** `hermes:desktop:zoomLevel`
- **Save function:** `setAndPersistZoomLevel(window, zoomLevel)` (line 3530)
- **Restore function:** `restorePersistedZoomLevel(window)` (line 3541)
- Restores on `did-finish-load` event (line 5269)

### How zoom is saved
When the user presses Ctrl/Cmd + =, -, or 0:
1. `installZoomShortcuts()` (line 3555) intercepts via `before-input-event`
2. Calls `setAndPersistZoomLevel()` which:
   - Clamps the zoom level
   - Calls `webContents.setZoomLevel(next)`
   - Writes to localStorage via `executeJavaScript`

### Keyboard shortcut quirk (IMPORTANT)

The handler checks `input.shift` and **rejects** the keypress if Shift is held:

```javascript
const mod = IS_MAC ? input.meta : input.control
if (!mod || input.alt || input.shift) return  // ← rejects Shift
```

This means:
- ✅ **Ctrl + =** (without Shift) → zoom in, persists
- ✅ **Ctrl + -** → zoom out, persists
- ✅ **Ctrl + 0** → reset to 100%, persists
- ❌ **Ctrl + Shift + =** (which produces `+`) → REJECTED (shift check)
- ❌ **Ctrl + Numpad +** → NOT handled (key is 'Add', not '=' or '+')

**Tell the user:** "Use Ctrl + = (the equals key, without Shift) to zoom in."

### If zoom doesn't persist

Possible causes:
1. User is pressing Ctrl+Shift++ (rejected by handler)
2. User is using Numpad + (not handled)
3. localStorage write failed silently (check desktop.log for `[zoom] persist failed`)
4. The app version doesn't have this code yet (check install stamp)

### Related settings that DO persist via JSON files

| Setting | File in userData | Mechanism |
|---------|-----------------|-----------|
| Theme (dark/light) | `native-theme.json` | `readPersistedThemeSource()` / `writePersistedThemeSource()` |
| Translucency | `translucency.json` | `readPersistedTranslucency()` / `writePersistedTranslucency()` |
| Connection | `connection.json` | Electron IPC |
| Active profile | `active-profile.json` | Electron IPC |
| Zoom | localStorage `hermes:desktop:zoomLevel` | `executeJavaScript` injection |

### File locations

- **Electron userData:** `%APPDATA%/Hermes/` (Windows) or `~/Library/Application Support/Hermes/` (macOS)
- **Hermes home:** `%LOCALAPPDATA%/hermes/` (Windows) or `~/.hermes/` (Linux/Mac)
- **Desktop log:** `<hermes_home>/logs/desktop.log`
