# Chrome MV3 Brave-like adblock extension

Session-derived recipe for recreating Brave-like ad blocking in Chrome without UI.

## Why not copy Brave Shields directly

Brave Shields is browser-native and powered by Brave's `adblock-rust` engine. It runs inside Brave, outside extension APIs. Chrome extensions cannot install that native integration. Closest Chrome-compatible recreation is Manifest V3 `declarativeNetRequest` plus cosmetic CSS.

## Practical architecture

```text
extension/
  manifest.json
  cosmetic.css
  rulesets/
    ruleset_1/ruleset_1.json
    ruleset_2/ruleset_2.json
    ...
```

`manifest.json` shape:

```json
{
  "manifest_version": 3,
  "name": "Brave-like Blocker for Chrome (Local)",
  "version": "1.0.0",
  "permissions": ["declarativeNetRequest"],
  "host_permissions": ["<all_urls>"],
  "declarative_net_request": {
    "rule_resources": [
      {"id": "ruleset_1", "enabled": true, "path": "rulesets/ruleset_1/ruleset_1.json"}
    ]
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "css": ["cosmetic.css"],
    "run_at": "document_start"
  }]
}
```

## Filter sources used

Good starter set:

- EasyList: `https://easylist.to/easylist/easylist.txt`
- EasyPrivacy: `https://easylist.to/easylist/easyprivacy.txt`
- uBlock filters: `https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/filters.txt`
- uBlock badware: `https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/badware.txt`
- uBlock privacy: `https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/privacy.txt`
- uBlock quick fixes: `https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/quick-fixes.txt`

Use a browser-like `User-Agent` when downloading EasyList; otherwise some requests may get `HTTP Error 403: Forbidden`.

## Conversion tool

`@adguard/tsurlfilter` can convert ABP/AdGuard-style network filters to Chrome DNR static rulesets:

```sh
npm init -y
npm i @adguard/tsurlfilter --no-audit --no-fund
npx tsurlfilter convert ./filters /resources ./extension/rulesets --prettify-json false
```

Input naming convention matters: filter files should be named like `filter_1.txt`, `filter_2.txt`, etc. Include `filters/filters.json` metadata.

## Windows pitfall

`tsurlfilter` expects `resourcesPath` to be a web-accessible extension path beginning with `/`, e.g. `/resources`. Some versions resolve the CLI argument to an absolute Windows path internally, causing:

```text
ResourcesPathError: Path to web accessible resources should be started with leading slash: C:\\...
```

Fast workaround for local one-off builds: patch installed `node_modules/@adguard/tsurlfilter/dist/cli.js` in `convertFilters`:

```js
const resourcesPath = resourcesDir;
```

Then call CLI with `/resources`.

## Chrome DNR cleanup

Converter output may include a metadata ruleset (`ruleset_0`) and `metadata` fields inside rule objects. Chrome DNR may reject these. Before generating manifest:

- skip `ruleset_0`
- remove `metadata` from each DNR rule object
- include only JSON arrays whose first item has `condition` and `action`

Python cleanup pattern:

```py
arr = json.loads(path.read_text(encoding="utf-8"))
if path.parent.name == "ruleset_0":
    continue
for rule in arr:
    rule.pop("metadata", None)
path.write_text(json.dumps(arr, separators=(",", ":")), encoding="utf-8")
```

## Cosmetic CSS extraction

Plain CSS content script can cover generic cosmetic rules only:

- accept lines starting with `##`
- skip exceptions `#@#`
- skip procedural/scriptlet rules: `#?#`, `#$#`, `##+js`, `:contains`, `:matches-css`, `:xpath`, `:style`, `:has-text`, etc.
- generate `selector { display: none !important; }`

This hides many ad slots but is not full Brave/uBO cosmetic parity.

## Verification

On Windows Git Bash:

```sh
"/c/Program Files/Google/Chrome/Application/chrome.exe" --pack-extension="C:\\Users\\ELY\\Desktop\\COSAS\\chrome-brave-blocker\\extension"
```

Expected: exit code `0` and `.crx`/`.pem` files created next to extension folder.

Also inspect manifest and rule files:

```py
import json, pathlib
m=json.loads(pathlib.Path('extension/manifest.json').read_text())
for r in m['declarative_net_request']['rule_resources']:
    a=json.loads((pathlib.Path('extension')/r['path']).read_text())
    assert all('metadata' not in x for x in a[:20])
```

## User install steps

Tell user:

1. Open `chrome://extensions/`.
2. Enable Developer mode.
3. Click “Load unpacked” / “Cargar descomprimida”.
4. Select exact extension folder.
5. If Chrome shows an error, send screenshot.
