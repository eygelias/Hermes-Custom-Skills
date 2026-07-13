# Blizzard Patch API Reference

## Endpoints

Base URL: `http://us.patch.battle.net:1119`

| Game | Path |
|---|---|
| Anniversary / TBC | `/wow_anniversary` |
| MOP Classic | `/wow_classic` |
| Era Classic | `/wow_classic_era` |

Sub-paths: `/versions`, `/cdns`

## Response Format

Pipe-separated (`|`), first line is header, subsequent lines are data.

### Versions
```
Region!STRING:0|BuildConfig!HEX:16|CDNConfig!HEX:16|KeyRing!HEX:16|BuildId!DEC:4|VersionsName!String:0|ProductConfig!HEX:16
us|bc3b8e61b6ba9f06|2374bc9b22181d36||68101|2.5.5.68101|92cbb948
eu|bc3b8e61b6ba9f06|2374bc9b22181d36||68101|2.5.5.68101|92cbb948
```

Columns (0-indexed): Region(0), BuildConfig(1), CDNConfig(2), KeyRing(3), BuildId(4), VersionsName(5), ProductConfig(6)

### CDNs
```
Region!STRING:0|BuildConfig!HEX:16|CDNPath!String:0|Host1!String:0|Host2!String:0|KeyRing!HEX:16
us|tpr/wow|level3.blizzard.com|cdn.blizzard.com|...
```

Columns: Region(0), BuildConfig(1), CDNPath(2), Host1(3), Host2(4), KeyRing(5)

## Regions
us, eu, cn, tw, kr, sg

## Important Notes
- Endpoint uses HTTP (not HTTPS), port 1119
- Android 9+ blocks cleartext HTTP by default — needs network_security_config.xml
- Cloudflare Worker can proxy this to provide HTTPS to the app
- CDN hosts field may contain spaces within URLs (separated by space, not pipe)
