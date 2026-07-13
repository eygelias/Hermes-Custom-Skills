# Electron destroyed-window teardown race

## Symptom

Windows Electron dialog:

```text
A JavaScript error occurred in the main process
Uncaught Exception:
TypeError: Object has been destroyed
    at readTitle
    at Timeout._onTimeout
```

Observed in Hermes Desktop after repeated backend restarts/update handoff. Logs still showed backend readiness, so treat as main-process UI teardown race first, not user data loss.

## Debug path

1. Check `~/.hermes/logs/desktop.log` (Windows install often maps to `%LOCALAPPDATA%/hermes/logs/desktop.log`).
2. Search `apps/desktop/electron/` for timer callbacks touching `BrowserWindow`/`webContents`:
   - `setTimeout(`
   - `BrowserWindow`
   - `getTitle()`
   - `isDestroyed`
3. For link-title resolution, inspect:
   - `electron/link-title-window.cjs`
   - `electron/main.cjs::runRenderTitleJob`
4. Compare source vs packaged build. Source may already be fixed while `release/win-unpacked/resources/app.asar` is stale. If so, rebuild/relaunch Desktop before chasing more code.

## Durable fix pattern

Put teardown-sensitive reads behind one helper:

```js
function readLinkTitleWindowTitle(window) {
  try {
    if (!window || window.isDestroyed()) return ''
    const contents = window.webContents
    if (!contents || contents.isDestroyed()) return ''
    return contents.getTitle() || ''
  } catch {
    return ''
  }
}
```

Then timers call helper instead of touching `window.webContents.getTitle()` directly:

```js
const finishWithTitle = () => finish(readLinkTitleWindowTitle(window))
hardTimer = setTimeout(finishWithTitle, RENDER_TITLE_TIMEOUT_MS)
```

Also clear timers and destroy defensively inside `finish()`.

## Verification

Run focused test, not whole desktop platform suite when triaging this specific class:

```bash
cd apps/desktop
node --test electron/link-title-window.test.cjs
```

Expected: all link-title-window tests pass, including destroyed-window/getTitle-throws cases.
