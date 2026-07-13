# Blizzard WoW Patch API

## Endpoint
`http://us.patch.battle.net:1119`

**Note**: HTTP only (no HTTPS). Port 1119. Android blocks this by default (see android-development skill).

## Paths
- `/wow_anniversary/versions` + `/wow_anniversary/cdns` — Anniversary/TBC
- `/wow_classic/versions` + `/wow_classic/cdns` — MOP Classic
- `/wow_classic_era/versions` + `/wow_classic_era/cdns` — Classic Era

## Response Format

### Versions
```
Region!STRING:0|BuildConfig!HEX:16|CDNConfig!HEX:16|KeyRing!HEX:16|BuildId!DEC:4|VersionsName!String:0|ProductConfig!HEX:16
## seqn = 3815170
us|bc3b8e61b6ba9f0686029dca74271889|2374bc9b22181d368eab210a0374bdf0||68101|2.5.5.68101|92cbb948f8b043dc019e4447149478d5
eu|bc3b8e61b6ba9f0686029dca74271889|2374bc9b22181d368eab210a0374bdf0||68101|2.5.5.68101|92cbb948f8b043dc019e4447149478d5
```

### CDNs
```
Region!STRING:0|BuildConfig!HEX:16|CDNPath!String:0|Host1!String:0|Host2!String:0|KeyRing!HEX:16
## seqn = 3815170
us|tpr/wow|level3.blizzard.com cdn.blizzard.com|http://level3.blizzard.com/?maxhosts=8 ...|tpr/configs/data
```

## Parsing

**CRITICAL**: Fields are `|` (pipe) separated, NOT space-separated!

```javascript
// Correct
const parts = line.trim().split("|");
const region = parts[0];        // "us"
const buildConfig = parts[1];   // hex hash
const buildId = parts[4];       // "68101"
const versionName = parts[5];   // "2.5.5.68101"

// WRONG — this was the bug that cost hours
const parts = line.trim().split("\\s+"); // ❌ Spaces are not the delimiter
```

First line is column headers (skip). Lines starting with `##` are metadata (skip).

## Region Order
us, eu, cn, tw, kr, sg
