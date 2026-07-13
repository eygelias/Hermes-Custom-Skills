---
name: network-equipment-analysis
description: Analyze consumer/SOHO network equipment (routers, ONTs, switches, access points) via their web management interfaces — identify hardware, firmware, chipsets, assess firmware replaceability, and extract configuration.
category: networking
triggers:
  - router analysis
  - ONT analysis
  - GPON equipment
  - BT-PON
  - WOW venezuela
  - BT-G113
  - firmware replacement assessment
  - network equipment inspection
  - router chipset identification
  - ISP equipment reuse
---

# Network Equipment Analysis

Analyze consumer/SOHO network equipment via their web management interfaces. Covers routers, ONTs (GPON/EPON), switches, and access points.

## Approach

### 1. Access the Web Interface

Common addresses: `192.168.100.1`, `192.168.1.1`, `192.168.0.1`, `10.0.0.1`.

**Pitfall — Login lockout**: Many ISP routers lock out after 3-5 failed attempts (30+ min). Always research default credentials BEFORE brute-forcing. Use `browser_vision` on blank pages — lockout messages may render with no interactive elements.

**Pitfall — Frameset-based interfaces**: Many legacy/embedded devices use HTML `<frameset>` (not `<iframe>`). Browser tools cannot click through frameset navigation links. Fix:
- Use `browser_console` to identify frame URLs: `document.querySelectorAll('frame')` or check `frames` object
- Navigate directly to content frame URLs (e.g., `/cgi-bin/sta-device.asp`)
- Or use `curl` with cookies to fetch pages directly

**Pitfall — Cookie-based authentication**: Many embedded devices authenticate via client-side JavaScript setting cookies (UID, PSW, SESSIONID, TOKEN), NOT via server-side POST form submission. Fix:
- Use the browser to log in (lets JS set cookies)
- Then extract cookies via `document.cookie` in console
- Use those cookies with curl for bulk page scraping
- Or navigate frame URLs directly in the browser after login

**Pitfall — Shell quoting with curl cookies**: Passing `-b "UID=x; TOKEN=y"` in bash breaks because semicolons are shell metacharacters. Fix:
- Use a Netscape cookie file: `curl -s -c cookies.txt URL` to capture server-set cookies, then append manual cookies with `echo "host\tFALSE\t/\tFALSE\t0\tNAME\tVALUE" >> cookies.txt`
- Or use `curl -b "UID=x" -b "TOKEN=y"` (separate `-b` flags per cookie)

**Pitfall — Short cookie lifetime on embedded devices**: SESSIONID/TOKEN cookies on ISP equipment often expire within minutes. Always re-login before bulk page fetching. Don't assume cookies from 5 minutes ago still work.

### 2. Extract Device Information

**Check user privilege level first.** ISP equipment often has multiple accounts (user/operador/admin/root) with different feature visibility. The `pageMap` array in `content.asp` reveals which features are enabled for the current user — if critical pages are hidden (`pageMap[X][Y] = "0"`), you need higher privileges before the analysis is complete.

Priority pages to check (URL patterns vary by vendor):
- **Device info**: `sta-device.asp`, `status.asp`, `device_info.asp`
- **WAN/network info**: `sta-network.asp`, `wan_info.asp`, `net-wanset.asp`
- **GPON config**: `app-gponconfig.asp`, `gpon_config.asp`
- **System/upgrade**: `upgrade.asp`, `backup_restore.asp`, `sys_upgrade.asp`
- **Menu/navigation JS**: `menu*.js`, `util*.js` — reveals all available pages and feature flags

Key fields to extract:
- Model, Serial Number, Hardware Version, Software/Firmware Version
- Manufacturer OUI (first 3 octets of MAC — identifies chip vendor)
- GPON SN (for ONT equipment)
- Compilation date (reveals firmware age)
- CPU/memory usage (reveals platform capability)

### 3. Assess Firmware Replaceability

**GPON/EPON ONTs** — Almost never replaceable:
- OLT (ISP-side equipment) validates: SN, GPON password, LOID
- ISP controls registration — changing ISP requires new credentials AND OLT must accept the hardware model
- TR-069 remote management means ISP can overwrite any local changes
- No community firmware exists for ISP-specific ONTs

**Consumer Routers** — Sometimes replaceable:
- Check if OpenWrt/LEDE supports the model (openwrt.org/toh)
- Look for firmware download on manufacturer site
- Check if bootloader (U-Boot) is accessible via serial console

### 4. Chipset Identification (Indirect)

Web interfaces rarely expose chipset directly. Clues:
- **Manufacturer OUI** in MAC address → lookup at macvendors.com
- **Firmware filename**: `tclinux` = Skyworth/ZTE platform; `.img` = varies
- **JS/CSS file names**: often contain platform hints (e.g., `menu_skyw.js` = Skyworth)
- **Feature set**: WiFi standards, port count, VoIP support → narrows chipset candidates
- **CPU/memory usage**: reveals embedded platform capability
- **Serial console** (if accessible): `dmesg`, `/proc/cpuinfo` give exact chipset

Common GPON ONT chipsets:
- Realtek RTL9601D/RTL9607C (low-end, very common in ISP equipment)
- Broadcom BCM68380/BCM68580 (mid-range)
- MediaTek MT7520/MT7621 (some models)

## Vendor-Specific Notes

### Skyworth (GN series)
- Firmware format: `tclinux`
- Menu JS: `menu_skyw.js`, `util_skyw.js`
- Content frame: `content.asp` with `pageMap` array controlling visible features
- Authentication: cookie-based (UID/PSW/SESSIONID/TOKEN)
- GPON config: `/cgi-bin/app-gponconfig.asp`
- Upgrade: `/cgi-bin/upgrade.asp` (accepts `tclinux` firmware or `romfile.cfg` config)
- **Fibex ISP (GN630V)**: See `references/fibex-gn630v-credentials.md` for credentials, page URLs, and permission structure

### BT-PON (BT series)
- Common ISP-issued ONTs in Latin America
- Default: admin/admin (credentials may not be on label)
- IP: 192.168.1.1
- **WOW Venezuela (BT-G113)**: See `references/wow-bt-g113-credentials.md`

### Huawei (HG series)
- Often uses TR-069 heavily
- Firmware may be signed — prevents unofficial flashing
- Superadmin credentials sometimes available for ISP models

### ZTE (F series)
- Similar to Skyworth (shared ODM heritage)
- `tclinux` firmware format common
- CLI access sometimes available via telnet

## Output Template

When analyzing equipment, produce a table with:
| Field | Value |
|---|---|
| Model | |
| Manufacturer | |
| Hardware Version | |
| Software Version | |
| Serial Number | |
| GPON SN (if ONT) | |
| OUI / MAC | |
| Compilation Date | |

Then a **firmware replaceability assessment** with clear verdict: Possible / Difficult / Impossible, and why.
