# Chrome MV3 YouTube Adblock Session Notes

## Context

User wanted Chrome to behave like Brave's built-in ad blocker, especially for YouTube ads, without needing a visible UI. User had Brave installed locally, so Brave's own adblock updater lists could be inspected.

## Durable Findings

- Brave Shields cannot be copied 1:1 into Chrome as an extension. Brave blocks with native browser integration (`adblock-rust`), while Chrome MV3 extensions are limited by `declarativeNetRequest` and content scripts.
- MV3 DNR rules built from EasyList/EasyPrivacy/uBlock lists block many ads/trackers but do not reliably block YouTube in-stream ads.
- Chrome's managed extension folder (`Chrome/User Data/Default/Extensions`) is not safe for unpacked source; Chrome may delete unmanaged folders. Use a stable folder such as `%LOCALAPPDATA%/<project>/extension` or a project directory.
- GitHub distribution should be a Release ZIP containing the `extension/` folder plus install docs. Users still load it unpacked via `chrome://extensions/`; arbitrary GitHub `.crx` is not equivalent to Chrome Web Store install.

## Brave Component Clues

Brave user data contains adblock updater components with `list.txt`, for example:

- `Brave Default Adblock Filters (plaintext)`
- `Brave Default Privacy Filters (plaintext)`
- `Brave First Party Adblock Filters (plaintext)`
- regional language blockers
- resources/scriptlet component

Useful YouTube rules seen in Brave/uBO-style lists include:

```txt
trusted-replace-fetch-response: "adPlacements" -> "no_ads"
trusted-replace-fetch-response: "adSlots" -> "no_ads"
trusted-replace-xhr-response: prune adPlacements/adSlots/adBreakHeartbeatParams
set ytInitialPlayerResponse.playerAds undefined
set ytInitialPlayerResponse.adPlacements undefined
set ytInitialPlayerResponse.adSlots undefined
set playerResponse.adPlacements undefined
json-prune playerResponse.adPlacements playerResponse.playerAds playerResponse.adSlots adPlacements playerAds adSlots
json-prune-fetch-response adPlacements adSlots playerResponse.adPlacements playerResponse.adSlots
json-prune-xhr-response adPlacements adSlots playerResponse.adPlacements playerResponse.adSlots
```

Chrome implementation approximation:

- `content_scripts[].world = "MAIN"`
- `run_at = "document_start"`
- hook `fetch`, `XMLHttpRequest`, `Response.prototype.json`, and sometimes `JSON.parse`
- protect/set-clean `window.ytInitialPlayerResponse` and `window.playerResponse`
- prune keys: `adPlacements`, `playerAds`, `adSlots`, `adBreakHeartbeatParams`, `adEngagementPanels`, `adSafetyReason`, `adTracking`

This may still not match Brave because Brave can apply native networking/scriptlet/resource behavior earlier and more deeply.

## Failure Pattern Seen

1. Generated local MV3 extension with DNR rulesets and global cosmetic CSS.
2. YouTube ads still appeared.
3. Added YouTube content script with DOM removal/CSS/fast-forward.
4. User reported YouTube search box could be clicked but immediately lost focus / could not type.
5. Removing `content_scripts` made search work again, proving injected JS/CSS caused focus regression.
6. Safer content script needed active-input guard and narrow URL scope.
7. Better Brave-like attempt used MAIN-world `document_start` response pruning instead of DOM/CSS manipulation.

## Safe YouTube Skipper Pattern

If using fallback skip/fast-forward, keep it narrow and non-destructive. Guard active input and avoid broad DOM removal:

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

## Avoid

- Global `cosmetic.css` on `<all_urls>` for YouTube/SPAs.
- Removing broad nodes (`.video-ads`, overlays, iframes) in a tight MutationObserver loop unless verified.
- `pointer-events: none`/visibility hacks that may cover controls.
- Repeated `video.currentTime = duration` without input/focus guards.
- Claiming Chrome extension can be identical to Brave Shields for YouTube.
- Putting unpacked extension source under Chrome's managed `User Data/.../Extensions` tree.

## User-Facing Debug Sequence

1. Ask user to press **Actualizar** in `chrome://extensions/` after each extension edit.
2. Have them close/reopen YouTube tabs.
3. If UI breaks, temporarily remove `content_scripts` and verify page works.
4. Add content script back only after narrowing scope and adding active-input guard.
5. For GitHub delivery, create Release with ZIP asset and explicit unpacked-load instructions.
