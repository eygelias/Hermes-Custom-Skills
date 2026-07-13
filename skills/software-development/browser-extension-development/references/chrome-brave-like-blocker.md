# Chrome Brave-like blocker recipe (session note)

Use when user asks to recreate Brave-style blocking in Chrome, especially with YouTube ads.

## Key findings

- Brave Shields are native browser integration powered by Brave's adblock engine (`adblock-rust`). Chrome extensions cannot copy this 1:1.
- Chrome MV3 blockers should use `declarativeNetRequest` for network blocking plus content scripts/CSS for cosmetic hiding.
- YouTube ads can survive DNR because some are delivered as first-party/player traffic. Add a YouTube content script to click Skip/Omitir/Saltar, hide ad overlays, mute/fast-forward `.ad-showing` playback.
- Do **not** place unpacked extension sources under:
  `C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\Extensions\...`
  Chrome owns that directory and may delete manual folders. Put local extension source in stable location like:
  `C:\Users\<user>\AppData\Local\chrome-brave-blocker-local\extension`

## Practical build pattern

1. Download lists:
   - EasyList
   - EasyPrivacy
   - uBlock filters
   - uBlock badware
   - uBlock privacy
   - uBlock quick fixes
2. Convert network rules to Chrome MV3 DNR using existing converter (e.g. AdGuard `@adguard/tsurlfilter`).
3. Strip converter-only metadata from rule JSON before Chrome load.
4. Generate `manifest.json` with:
   - `permissions: ["declarativeNetRequest"]`
   - `host_permissions: ["<all_urls>"]`
   - `declarative_net_request.rule_resources`
   - `content_scripts` for CSS and YouTube helper JS.
5. Generate `cosmetic.css` from generic ABP cosmetic rules only; skip procedural/scriptlet selectors that normal CSS cannot parse.
6. Add `youtube.js` content script:
   - remove/hide `#player-ads`, `ytd-ad-slot-renderer`, `.ytp-ad-overlay-container`, `.video-ads`, DoubleClick/Google ad iframes.
   - click visible `.ytp-ad-skip-button`, `.ytp-ad-skip-button-modern`, buttons with labels containing Skip/Saltar/Omitir.
   - when `.ad-showing` exists: mute video, set `playbackRate = 16`, seek near duration end, then click skip again.

## Windows pitfalls

- Python `subprocess.run(["npx", ...])` may fail on Windows; use `npx.cmd`.
- Some converters expect web-accessible resource paths starting with `/resources`, not absolute Windows paths.
- Repack verification:

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" --pack-extension="C:\path\to\extension"
```

Use `--pack-extension-key="C:\path\to\extension.pem"` to keep same packed extension ID.

## Verification checklist

- Parse `manifest.json` successfully.
- Confirm version incremented after code changes.
- Confirm `youtube.js` exists and is listed in `content_scripts`.
- Confirm all `rule_resources[].path` exist.
- Confirm DNR rule objects do not contain stray `metadata` fields.
- Pack extension with Chrome and check exit code 0.
- Tell user to click `Actualizar` in `chrome://extensions/`, then close/reopen YouTube tabs.
