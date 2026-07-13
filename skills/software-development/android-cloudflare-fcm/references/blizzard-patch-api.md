# Blizzard WoW Patch API

**Base URL**: `http://us.patch.battle.net:1119`

## Endpoints

| Game | Path |
|------|------|
| Anniversary/TBC | `/wow_anniversary` |
| MOP Classic | `/wow_classic` |
| Era Classic | `/wow_classic_era` |

For each game: `{path}/versions` and `{path}/cdns`

## Data Format (pipe-separated, NOT space-separated)

### Versions
```
Region!STRING:0|BuildConfig!HEX:16|CDNConfig!HEX:16|KeyRing!HEX:16|BuildId!DEC:4|VersionsName!String:0|ProductConfig!HEX:16
us|bc3b8e61b6ba9f06|2374bc9b22181d36||68101|2.5.5.68101|92cbb948...
eu|bc3b8e61b6ba9f06|2374bc9b22181d36||68101|2.5.5.68101|92cbb948...
```

Columns (0-indexed, split by `|`):
- `[0]` = Region code (us, eu, cn, tw, kr, sg)
- `[1]` = BuildConfig hash
- `[2]` = CDNPath
- `[3]` = KeyRing
- `[4]` = BuildId (numeric)
- `[5]` = VersionsName (e.g., "2.5.5.68101")
- `[6]` = ProductConfig hash

### CDNs
```
us|tpr/wow|level3.blizzard.com us.cdn.blizzard.com|http://level3.blizzard.com/...|tpr/configs/data
```

Columns:
- `[0]` = Region
- `[1]` = CDNPath
- `[2]` = CDN hosts (space-separated within the field!)
- `[3]` = CDN URLs with params
- `[4]` = KeyRing path

## Pitfalls

- **Data uses `|` as separator**, NOT whitespace. Code that does `split("\\s+")` will find 0 regions.
- **First line is column headers** — skip it (`.drop(1)` or `.slice(1)`)
- **Lines starting with `##` are metadata** — filter them out
- **Only works over HTTP** (port 1119), NOT HTTPS. Android blocks this by default — use `network_security_config.xml` or proxy via Cloudflare Worker
- **Region order**: us, eu, cn, tw, kr, sg (no fixed order in API response)
