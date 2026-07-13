---
name: browser-extension-development
description: Build, debug, package, and verify browser extensions for Chrome/Chromium/Firefox, including Manifest V3, declarativeNetRequest, content scripts, and local unpacked installs.
triggers:
  - Chrome extension
  - browser extension
  - Manifest V3
  - declarativeNetRequest
  - content script
  - ad blocker extension
  - unpacked extension
  - Brave-like blocker
---

# Browser Extension Development

Use when building or debugging browser extensions, especially Chrome/Chromium Manifest V3 extensions.

## Workflow

1. Confirm browser target and extension model:
   - Chrome/Chromium: Manifest V3 preferred/required.
   - Firefox: may support different APIs and MV2/MV3 behavior.
2. Prefer native browser APIs before custom engines:
   - Network blocking: `declarativeNetRequest` for Chrome MV3.
   - DOM/CSS changes: `content_scripts` with CSS/JS.
   - Persistent background logic: MV3 service worker.
3. Keep extension minimal:
   - `manifest.json`
   - content scripts/styles
   - static rulesets or small service worker
   - no UI unless user asked.
4. Verify with real browser tooling or Chrome packaging:
   - Load unpacked via `chrome://extensions/`.
   - Or run Chrome `--pack-extension=<folder>` to validate basic packaging.
5. Leave user-facing install steps with exact folder path.

## Chrome MV3 ad-blocking pattern

Chrome cannot embed a native browser-level blocker like Brave Shields. Recreate maximum allowed behavior with:

- `declarativeNetRequest` static rulesets for network blocking.
- Filter-list conversion from EasyList/uBlock/AdGuard syntax to DNR JSON.
- `content_scripts` CSS for cosmetic hiding, but never as broad `<all_urls>` without checking focus/click behavior.
- No extension UI if user wants silent behavior.

See `references/chrome-mv3-brave-like-adblock.md` for concrete build recipe and pitfalls.
See `references/brave-youtube-adblocking-notes.md` for Brave/uBO YouTube response-cleaning patterns and limits.

## YouTube / Brave Shields parity

Do not promise exact Brave behavior for YouTube in Chrome. Brave can use native Shields/adblock-rust plus trusted scriptlets/response rewriting earlier than a Chrome extension may run. For YouTube:

1. Start with DNR/network rules.
2. If ads remain, implement a `world: "MAIN"` content script at `document_start` that prunes YouTube player responses (`adPlacements`, `playerAds`, `adSlots`, `adBreakHeartbeatParams`) from `fetch`, `XMLHttpRequest`, `Response.prototype.json`, `JSON.parse`, `ytInitialPlayerResponse`, and `playerResponse`.
3. Only add a guarded skip-button fallback after response-cleaning; never make it the primary “Brave-like” claim.
4. Guard any fallback against active search/input focus. YouTube search losing caret/focus is a strong signal that the content script is too aggressive.

## Pitfalls

- Brave Shields uses `adblock-rust` inside the browser. Chrome extensions cannot copy that exact integration.
- Chrome MV3 blocks via DNR, not arbitrary synchronous request interception.
- DNR JSON must contain valid Chrome rule objects only. Converter metadata fields can make Chrome reject rulesets.
- Domain-specific cosmetic/procedural filters (`:has-text`, scriptlets, `##+js`, etc.) need a real adblock engine or more complex content-script logic; plain CSS only covers generic CSS selectors.
- Do not promise 100% parity with Brave; say “maximum Chrome allows” unless building a custom Chromium fork.

## Windows notes

- In Git Bash/MSYS terminal, Chrome usually lives at `/c/Program Files/Google/Chrome/Application/chrome.exe`.
- Pack validation example:

```sh
"/c/Program Files/Google/Chrome/Application/chrome.exe" --pack-extension="C:\\path\\to\\extension"
```

## Done criteria

- Extension folder exists.
- `manifest.json` loads/validates.
- Rules/content scripts referenced by manifest exist.
- Packaging or browser load is attempted.
- Final answer includes exact install path and `chrome://extensions/` steps.
