# Fibex Telecom — Skyworth GN630V Credentials & Access Notes

## Known Credentials

| Username | Password | Level | Notes |
|----------|----------|-------|-------|
| `operador` | `operad0rFibex` | Root (ISP-customized) | Only account available on Fibex-branded units |

### Tested (all FAIL on Fibex units):
- `admin` / `admin` ❌
- `root` / `admin` ❌
- `telecomadmin` / `admintelecom` ❌

### Other ISPs (same GN630V model, different firmware):
- **Converge (Philippines)**: `admin` / `Converge@sky123` — superadmin with full access
- Generic Skyworth: username blank, password `admin`

## Login Lockout
- **3 failed attempts → 30-minute lockout**
- Error message: *"N errores, intételo después de 30 minutos."*
- The lockout page renders nearly blank (easy to miss — use `browser_vision` to confirm)

## Permission Restrictions on `operador` Account
Despite being labeled "root" in tutorials, the `operador` account has firmware-level restrictions:
- `pageMap[5][6] = "0"` → Firmware upgrade page HIDDEN
- `ssidNum` forced to `'0'` on 2.4G WLAN → can only edit SSID1
- WAN Binding page (`net-binding.asp`) → redirects to login (no access)
- User management, reboot, logs, backup → accessible

## Web Interface Quirks
- **Frameset-based**: `content.asp` loads a `<frameset>` with `refreshfrm` and `contentfrm`
- **Cookie auth**: Login sets `UID`, `PSW`, `SESSIONID`, `TOKEN` cookies via JavaScript
  - Cannot use `curl POST` to authenticate — must use browser for JS cookie flow
  - After browser login, `document.cookie` may return `null` in console (SecurityError) — use the cookies set in the earlier successful login
- **Frame navigation**: Menu links use JS to change `contentfrm.src` — `browser_click` on menu items sometimes doesn't update the visible content. Direct URL navigation to frame URLs also fails (redirects to login). Workaround: navigate to `/` (root) after login.
- **SESSIONID expiry**: Sessions expire relatively quickly (~5 min idle). Re-login frequently.

## Useful Direct URLs (require valid session cookies)
| Page | URL |
|------|-----|
| WLAN 2.4G config | `/cgi-bin/net-wlan.asp` |
| WLAN 5G config | `/cgi-bin/net-wlan11ac.asp` |
| WAN Binding | `/cgi-bin/net-binding.asp` |
| DHCP/LAN | `/cgi-bin/net-dhcp.asp` |
| MAC Filter | `/cgi-bin/sec-macfilter.asp` |
| ACL | `/cgi-bin/sec-acl.asp` |
| NAT | `/cgi-bin/app-natset.asp` |
| DMZ | `/cgi-bin/app-dmz.asp` |
| Port Forward | `/cgi-bin/app-portforwarding.asp` |
| Remote Mgmt | `/cgi-bin/app-remotemanagement.asp` |
| GPON Config | `/cgi-bin/app-gponconfig.asp` |

## SSID Structure (from `net-wlan.asp` JS)
- 2.4G has multiple SSIDs (up to 8) but `operador` only sees SSID1
- When `ssidNum == "4"` or `"8"`: SSID1="Vecino", SSID2="fibex", plus mesh backhaul SSIDs
- 5G: ssidArray includes "Vecino", "FIBEXTEL-3FCB_5Ghz_6/7/8", plus SKYMESH backhaul
- Mesh backhaul SSIDs (SKYMESH_*) are hidden management SSIDs

## No Hidden Superadmin for Fibex
Extensive web search confirmed: Fibex only provides the `operador` account. Unlike Converge (which has `admin`/`Converge@sky123` as a separate superadmin), Fibex customized the firmware to use a single account with limited permissions. The `operador` account IS the highest-privilege account available.
