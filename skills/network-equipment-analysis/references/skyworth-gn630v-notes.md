# Skyworth GPON ONT Analysis — Session Notes

## Skyworth GN630V (Fibex Telecom branded)

### Device Info
- Model: GN630V
- Manufacturer OUI: 084F66
- HW Version: V1.0
- SW Version: V1.0.0.4
- GPON SN format: SKYWB + 8 hex chars (e.g., SKYWB8071BFE)
- Compilation: 2024-06-24 14:58:30

### Web Interface Structure
- Login page: `/cgi-bin/index2.asp`
- Main frame: `/cgi-bin/content.asp` (defines `pageMap` array + loads frameset)
- Content frame name: `contentfrm`
- Refresh frame name: `refreshfrm`
- Menu JS: `/JS/menu_skyw.js?v=V1.0.0.4`
- Util JS: `/JS/util_skyw.js?v=V1.0.0.4`
- CSS: `/JS/stylemain_skyw.css?v=V1.0.0.4`

### Authentication Flow
1. GET `/cgi-bin/index2.asp` → server sets `TOKEN` + `SESSIONID` cookies
2. JavaScript sets `UID` and `PSW` cookies from form fields
3. Redirect to `/` which checks cookies and loads `/cgi-bin/content.asp`
4. Cannot use curl POST to authenticate — must use browser for JS cookie setting

### pageMap Feature Flags (from content.asp)
```
pageMap[1][1] = "1"  → Device Info
pageMap[1][2] = "1"  → WAN Info  
pageMap[1][3] = "1"  → LAN Info
pageMap[2][3] = "1"  → LAN (DHCP)
pageMap[2][4] = "1"  → WLAN 2.4G
pageMap[2][7] = "1"  → SNTP
pageMap[2][8] = "1"  → Routing
pageMap[2][10] = "1" → WLAN 5G
pageMap[2][11] = "1" → EasyMesh
pageMap[3][1-7]      → Security (URL/MAC/port filter, ACL, WAN access)
pageMap[4][1-3,8]    → Advanced (DDNS, NAT/DMZ/port forward, UPNP, GPON)
pageMap[5][1-3,5]    → System (users, reboot, logs, backup)
pageMap[5][6] = "0"  → Upgrade DISABLED (firmware upgrade hidden from operador user)
```

### WAN Configuration
- VLAN 200: TR069 (management, down)
- VLAN 100: INTERNET (up, DHCP, IPv4+IPv6)
- WAN MAC: 08:4F:66:7F:3F:CC

### Firmware Upgrade Page
- Accepts `tclinux` files (firmware) or `romfile.cfg` (config backup)
- Upload via `/cgi-bin/upgrade.asp`
- Config backup download: `/romfile.cfg`

### GPON Authentication Fields
- GPON Password (up to 10 ASCII or 20 hex chars)
- LOID (up to 24 ASCII chars)
- LOID Password
- All disabled when xPON link is up (`xpon_up == "1"`)

### Practical Interaction Notes (from session 2026-06-26)

#### Browser Automation Pitfalls
- The interface uses `<frameset>` (not iframe). Menu links (Estado, Red, WLAN, etc.) are JavaScript-driven — they change `contentfrm`'s `location.href` via `MakeMenu()`. Browser `browser_click` on menu links does NOT reliably navigate the content frame.
- **Workaround**: Navigate directly to content frame URLs (e.g., `http://192.168.100.1/cgi-bin/net-wlan.asp`). BUT the router redirects to `/cgi-bin/index2.asp` if cookies are stale.
- Login flow: POST to `index2.asp` → JavaScript sets `UID`, `PSW` cookies from form → redirect to `/` → server checks cookies → loads `content.asp` frameset. The SESSIONID cookie is generated server-side on GET of `index2.asp` (Set-Cookie header), NOT by JavaScript.

#### Curl Cookie Pitfall
- Shell quoting with semicolons in `-b` flag breaks bash. **Use a Netscape cookie file** instead:
  ```
  curl -s -c /tmp/ck.txt "http://192.168.100.1/cgi-bin/index2.asp"  # get TOKEN+SESSIONID
  # Then manually add UID/PSW to cookie file, or use browser to login and extract cookies
  ```
- Cookie lifetime is short (~minutes). Re-fetch pages promptly after login.

#### User Level Permissions (`operador` account)
- `ssidNum` for 2.4G WLAN page gets forced to `'0'` — only SSID1 is editable/visible.
- `ssidNum` for 5G WLAN page = `8` — but the stWlan data array only returns one entry (the first SSID).
- Binding page (`net-binding.asp`) redirects to login for `operador` — requires higher privilege.
- Upgrade page hidden (`pageMap[5][6] = "0"`).
- To see/edit ALL SSIDs, need `admin` or `root` level account.

#### SSID Configuration (observed 2026-06-26)
- **2.4G**: 1 user-visible SSID = `fibex` (WPA2-PSK, enabled, mode 16=g,n,ax)
- **5G**: Multiple SSIDs exist — `Vecino`, `FIBEXTEL-3FCB_5Ghz_6/7/8`, plus hidden SKYMESH mesh backhaul SSIDs.
- Total SSID capacity: 8 per band (ssidNum=8 in pageMap).
- SSID numbering in UI: SSID1=index 0 or 1 depending on ssidNum value. When ssidNum=="4"||"8", indices shift: SSID1=index 1, SSID2=index 2, etc.

#### WLAN Page URLs
- 2.4G: `/cgi-bin/net-wlan.asp`
- 5G: `/cgi-bin/net-wlan11ac.asp`
- EasyMesh: `/cgi-bin/wifi_multi_ap_basic.asp`
- WiFi Schedule: `/cgi-bin/wifi_schedule.asp`
- Guest Network: `/cgi-bin/wifi_guest.asp`
- Band Steering: `/cgi-bin/wifi_bandsteering.asp`

#### No Per-SSID Internet Control
- This router has NO built-in "disable internet for this SSID" option while keeping WiFi active.
- Possible approaches (untested, may require admin account):
  1. WAN Binding (`net-binding.asp`) — unbind SSID from Internet VLAN
  2. MAC Filter (`sec-macfilter.asp`) — block devices by MAC
  3. ACL (`sec-acl.asp`) — access control rules
  4. URL Filter (`sec-urlfilter.asp`) — block all URLs for specific source

### Firmware Replaceability Verdict: ❌ IMPOSSIBLE
- No public firmware alternative (no OpenWrt, no community builds)
- OLT authentication chain prevents ISP switching
- TR-069 allows ISP to remotely revert any changes
- `tclinux` format is proprietary to Skyworth ISP builds
- Firmware upgrade page was hidden for `operador` user level

### Permission Levels (ISP-customizable)
The `pageMap` array and `ssidNum` variable control feature visibility per user:
- `ssidNum = '0'` → only SSID1 editable (operador level)
- `ssidNum = '8'` → all 8 SSIDs editable (admin level)
- `pageMap[5][6] = '0'` → firmware upgrade hidden
- Binding page (`net-binding.asp`) → requires admin-level access, redirects to login for operador

### Known ISP Credential Patterns (same GN630V hardware)
| ISP | Username | Password | Access Level |
|-----|----------|----------|-------------|
| Fibex (Venezuela) | `operador` | `operad0rFibex` | Limited root (no binding, no firmware upgrade) |
| Converge (Philippines) | `admin` | `Converge@sky123` | Full superadmin |
| Converge user | `user` | varies | Basic user |

Fibex has NO hidden superadmin beyond `operador` — confirmed via web research and login testing.
