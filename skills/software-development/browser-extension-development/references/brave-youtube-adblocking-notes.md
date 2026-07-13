# Brave-like YouTube adblocking notes

Session-derived notes from building a local Chrome MV3 “Brave-like” blocker and comparing with installed Brave components.

## What Brave had locally

Brave adblock update components lived under:

- `%LOCALAPPDATA%/BraveSoftware/Brave-Browser/User Data/<component-id>/<version>/list.txt`
- `%LOCALAPPDATA%/BraveSoftware/Brave-Browser/User Data/<component-id>/<version>/resources.json`

Relevant component names observed:

- Brave Default Adblock Filters (plaintext)
- Brave Default Privacy Filters (plaintext)
- Brave First Party Adblock Filters (plaintext)
- Spanish website ad blocker (plaintext)
- Spanish and Portuguese website ad blocker (plaintext)
- Resources
- Query Filter

## YouTube rules Brave/uBO used

Important rule families seen in Brave default adblock lists:

```adblock
www.youtube.com##+js(trusted-replace-xhr-response, /"adPlacements.*?("adSlots"|"adBreakHeartbeatParams")/gms, $1, /\/player(?:\?.+)?$/)
www.youtube.com##+js(trusted-replace-fetch-response, '"adPlacements"', '"no_ads"', player?)
www.youtube.com##+js(trusted-replace-fetch-response, '"adSlots"', '"no_ads"', player?)
m.youtube.com,music.youtube.com,tv.youtube.com,www.youtube.com##+js(set, ytInitialPlayerResponse.playerAds, undefined)
m.youtube.com,music.youtube.com,tv.youtube.com,www.youtube.com##+js(set, ytInitialPlayerResponse.adPlacements, undefined)
m.youtube.com,music.youtube.com,tv.youtube.com,www.youtube.com##+js(set, ytInitialPlayerResponse.adSlots, undefined)
m.youtube.com,music.youtube.com,youtubekids.com,youtube-nocookie.com##+js(json-prune, playerResponse.adPlacements playerResponse.playerAds playerResponse.adSlots adPlacements playerAds adSlots important)
www.youtube.com##+js(json-prune-fetch-response, adPlacements adSlots playerResponse.adPlacements playerResponse.adSlots, , propsToMatch, /player?)
www.youtube.com##+js(json-prune-xhr-response, adPlacements adSlots playerResponse.adPlacements playerResponse.adSlots, , propsToMatch, /\/player(?:\?.+)?$/)
```

## Implementation pattern for Chrome extension approximation

Use `manifest.json` content script:

```json
{
  "matches": ["*://www.youtube.com/*", "*://m.youtube.com/*"],
  "js": ["yt-main.js"],
  "run_at": "document_start",
  "world": "MAIN",
  "all_frames": false
}
```

`yt-main.js` should run before app code and prune ad payloads from:

- `window.fetch`
- `XMLHttpRequest`
- `Response.prototype.json`
- `JSON.parse`
- `window.ytInitialPlayerResponse`
- `window.playerResponse`

Keys to prune:

- `adPlacements`
- `playerAds`
- `adSlots`
- `adBreakHeartbeatParams`
- `adEngagementPanels`
- `adSafetyReason`
- `playbackTracking.adTracking`

## Pitfalls found

- Global `cosmetic.css` over `<all_urls>` can break YouTube UI, including click/focus on search.
- Repeated loops that set video `currentTime`, click skip, or remove DOM can steal focus; the search caret appears then vanishes.
- DOM removal/CSS hiding may remove or cover useful elements. Prefer response pruning before UI hacks.
- If a fallback skip loop is used, guard it when `document.activeElement` is an input/search element.
- Loading unpacked extensions from Chrome-managed `User Data/Default/Extensions` is unstable; Chrome may delete custom folders. Use `%LOCALAPPDATA%/<extension-name>/extension` or a project path.

## User-facing expectation

Say clearly: Chrome MV3 can approximate Brave Shields, but exact YouTube parity may be impossible without Brave’s native integration or a full adblock engine. Do not overpromise “same as Brave” until verified on a fresh YouTube tab.
