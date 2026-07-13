---
name: chrome-extension-development
description: "Build and debug Chrome/Chromium extensions, especially Manifest V3 DNR/content-script blockers."
triggers:
  - Chrome extension
  - Chromium extension
  - Manifest V3
  - declarativeNetRequest
  - content script
  - ad blocker extension
  - extension breaks page input
---

# Chrome Extension Development

Use for building or debugging Chrome/Chromium extensions. Prefer existing browser APIs and smallest possible manifest before adding frameworks.

## Manifest V3 Basics

1. Keep `manifest.json` minimal.
2. For network blocking, prefer `declarativeNetRequest` static rulesets over background request logic.
3. Keep content scripts scoped to exact sites/paths; avoid `<all_urls>` unless required.
4. Use unpacked extension folders outside Chrome's managed profile directory. Do **not** store source under `User Data/Default/Extensions`; Chrome can delete/manage that tree.
5. After editing an unpacked extension, instruct user to press **Actualizar/Reload** in `chrome://extensions/`, then close/reopen affected tabs.

## Debugging Page Breakage

When extension causes page UI issues (search box loses focus, clicks fail, controls disappear):

1. Split extension behavior into buckets:
   - DNR/network rules
   - CSS injection
   - content-script DOM mutation
   - interval/timer automation
   - media manipulation
2. First test a safe manifest with **no `content_scripts`**. If page works, root cause is injected JS/CSS, not network blocking.
3. Reintroduce one bucket at a time.
4. Avoid global cosmetic CSS on complex SPAs. Broad selectors can hide/tap-block real UI.
5. Search for code that removes nodes, injects `pointer-events`, clicks buttons in loops, edits `currentTime`, or runs `MutationObserver`/`setInterval` too aggressively.
6. Protect active input before automation:

```js
const userTyping = () => {
  const el = document.activeElement;
  return el && (
    el.tagName === 'INPUT' ||
    el.tagName === 'TEXTAREA' ||
    el.isContentEditable ||
    el.closest?.('form, [role="search"], ytd-searchbox')
  );
};
if (userTyping()) return;
```

## YouTube Ad Blocking Reality Check

Chrome MV3 extensions cannot fully copy Brave Shields. Brave uses native browser-level `adblock-rust`; Chrome extensions are constrained by MV3 and YouTube first-party/stitched ad delivery.

Safe approach:

- Use DNR rules for normal ad/tracker blocking.
- If user asks to learn from Brave, inspect Brave's user-data adblock component lists (`Brave Ad Block Updater (...)` `list.txt`) for durable filter/scriptlet ideas rather than guessing.
- Brave/uBO YouTube rules commonly target `adPlacements`, `playerAds`, `adSlots`, `adBreakHeartbeatParams`, `ytInitialPlayerResponse`, `playerResponse`, `/youtubei/v1/player`, `/youtubei/v1/get_watch`, `fetch`, `XHR`, `Response.json`, and `JSON.parse`.
- For Chrome, run these as tightly scoped MAIN-world `document_start` scriptlets (`"world": "MAIN"`) only on YouTube if needed. Isolated-world content scripts cannot patch page-owned `fetch`/`JSON.parse` reliably.
- Keep fallback skip/fast-forward guarded and narrow; it may show a brief ad/skip button and is not equivalent to Brave.
- Do not inject broad CSS or remove arbitrary nodes on YouTube; it can break search and navigation.

## GitHub Release Pattern

For extensions distributed from GitHub, release a ZIP, not just source:

1. Put loadable files under an `extension/` folder.
2. Create `dist/<name>-vX.Y.Z.zip` containing the `extension/` folder and install docs.
3. Tag `vX.Y.Z`, create a GitHub Release, upload the ZIP asset.
4. Release notes must say: download ZIP → extract → `chrome://extensions/` → Developer mode → **Cargar extensión sin empaquetar** → select `extension`.
5. Do not promise direct GitHub install like Chrome Web Store; Chrome blocks normal installation of arbitrary external `.crx` packages.

## Verification Checklist

- `manifest.json` parses.
- Ruleset paths exist.
- Extension loads in `chrome://extensions/` without red errors.
- Target page UI still works with extension enabled.
- If content scripts exist, verify reload behavior after pressing extension **Actualizar**.
- For YouTube: verify search input focus/typing, video controls, and ad behavior separately.

## References

- `references/chrome-mv3-youtube-adblock.md` — session pattern: Brave-like Chrome blocker, YouTube ad limitations, input-focus regression, safe mitigation.
