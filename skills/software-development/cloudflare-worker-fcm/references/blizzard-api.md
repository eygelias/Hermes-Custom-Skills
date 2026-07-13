# Blizzard Patch Agent API

## Endpoints

Base: `http://us.patch.battle.net:1119`

| Game | Path |
|------|------|
| Anniversary / TBC | `/wow_anniversary` |
| MOP Classic | `/wow_classic` |
| Era Classic | `/wow_classic_era` |

For each game: `{path}/versions` and `{path}/cdns`.

## Response Format

**Uses `|` (pipe) as separator, NOT spaces.**

Header line (skip):
```
Region!STRING:0|BuildConfig!HEX:16|CDNConfig!HEX:16|KeyRing!HEX:16|BuildId!DEC:4|VersionsName!String:0|ProductConfig!HEX:16
```

Data line:
```
us|bc3b8e61b6ba9f0686029dca74271889|2374bc9b22181d368eab210a0374bdf0||68101|2.5.5.68101|92cbb948f8b043dc019e4447149478d5
```

Parsed columns (0-indexed, split by `|`):
- `[0]` = Region (us, eu, cn, tw, kr, sg)
- `[1]` = BuildConfig hash
- `[2]` = CDNPath
- `[3]` = KeyRing (often empty)
- `[4]` = BuildId (numeric)
- `[5]` = VersionsName (e.g. "2.5.5.68101")
- `[6]` = ProductConfig hash

CDNs line columns:
- `[0]` = Region
- `[1]` = BuildConfig
- `[2]` = CDNPath
- `[3]` = Host1
- `[4]` = Host2
- `[5]` = KeyRing

## Pitfall

Common mistake: splitting by `\s+` (whitespace). Must split by `|`. The original app code had this bug for several iterations.

## Region Order (preferred by WoW players)

us → eu → cn → tw → kr → sg

Flags: us=🌎, eu=🇪🇺, cn=🇨🇳, tw=🇹🇼, kr=🇰🇷, sg=🌏
