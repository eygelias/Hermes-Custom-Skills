---
name: android-adb
description: ADB device management — wireless debugging pairing, device backup via content providers, app inventory & optimization, device info extraction. For managing Android devices from PC, not building apps.
tags: [android, adb, debugging, backup, optimization, wireless]
triggers:
  - ADB wireless debugging
  - connecting phone to PC via ADB
  - Android device backup
  - uninstalling Android bloatware
  - optimizing Android device
  - ADB pair
  - phone not recognized by PC
---

# Android ADB Device Management

## Prerequisites

ADB must be installed. If not found, download platform-tools:
```bash
cd ~ && curl -L -o platform-tools.zip "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
unzip -o platform-tools.zip -d ~/ > /dev/null 2>&1
export PATH="$HOME/platform-tools:$PATH"
adb version
```

On Windows (git-bash/MSYS), always set PATH before any adb command:
```bash
export PATH="/c/Users/ELY/platform-tools:$PATH"
```

## Wireless Debugging Pairing (Android 11+)

### Problem
`adb pair` is interactive — it prompts for a pairing code. On Windows (git-bash), piping input fails:
```bash
# ❌ DOES NOT WORK on Windows
echo "123456" | adb pair 192.168.x.x:port
printf "123456\n" | adb pair 192.168.x.x:port
adb pair 192.168.x.x:port <<< "123456"
```
All produce: `error: protocol fault (couldn't read status message): No error`

PTY mode (`pty=true`) also doesn't work reliably for `adb pair`.

### Solution — Python subprocess wrapper
Write a small Python script to handle the interactive prompt:

```python
import subprocess, time

adb = r"C:\Users\ELY\platform-tools\adb.exe"
proc = subprocess.Popen(
    [adb, "pair", "192.168.100.249:41781"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

time.sleep(2)  # Wait for prompt
proc.stdin.write("917628\n")  # The pairing code
proc.stdin.flush()
proc.stdin.close()

try:
    out = proc.communicate(timeout=15)[0]
    print(out)
except subprocess.TimeoutExpired:
    proc.kill()
    print("TIMEOUT")
```

**Why `time.sleep(2)` is needed**: adb pair prints "Enter pairing code:" but the pipe isn't ready immediately. The sleep ensures the prompt is flushed before we write the code.

### Full Wireless Connection Workflow

**On the phone** (Settings → Developer Options → Wireless debugging):
1. Note the **IP Address & Port** (e.g., `192.168.100.249:37495`) — this is for `adb connect`
2. Tap **"Pair device with pairing code"** — shows a popup with:
   - **Pairing code** (6 digits, e.g., `917628`)
   - **Pairing IP & Port** (DIFFERENT from above, e.g., `192.168.100.249:41781`)
3. The pairing code changes if you close and reopen the popup

**On the PC**:
```bash
# Step 1: Pair (use the PAIRING port from the popup, NOT the main port)
# Use the Python script above — piping doesn't work on Windows

# Step 2: Connect (use the MAIN port from the wireless debugging screen)
adb connect 192.168.100.249:37495

# Step 3: Verify
adb devices -l
```

**Critical**: The pairing port and the connection port are DIFFERENT. The pairing port appears in the popup dialog; the connection port is shown on the main wireless debugging screen.

### Pitfalls
- **ADB daemon restart kills connection** — when running via `execute_code`, each new Python subprocess can restart the adb daemon and lose the device connection (`device not found`). Always run ALL adb commands in a **single bash `terminal()` session** with a multi-line script, not multiple `execute_code` calls.
- **mDNS device names after pairing** — after wireless pairing, the device may appear as `adb-XXXXX._adb-tls-connect._tcp` instead of `IP:PORT`. The IP:PORT may show as `offline` while the mDNS name shows as `device`. Use the mDNS name for `-s` flag: `adb -s "adb-XXXXX._adb-tls-connect._tcp" shell ...`. Quote the name because of dots and underscores.
## Pitfalls
- **Pairing codes expire** — if the popup closes or you wait too long, get a fresh code
- **Phone and PC must be on the same WiFi network** — verify with `ping <phone-ip>`
- **Firewall may block** — Windows Firewall can block ADB connections; allow `adb.exe` through
- **After reboot, re-pair** — wireless debugging pairing doesn't always survive reboots
- **Port changes** — wireless debugging port can change even without reboot; if `adb connect` fails with "connection refused", ask user for the new port
- **Batch operations lose connection** — when running 20+ adb commands via Python subprocess, the daemon restarts and drops the device. Use bash loops via `terminal()` instead. See `android-device-optimization` skill for details.
- **Settings commands fail on wireless** — `settings put global/secure/system` requires WRITE_SECURE_SETTINGS which is NOT granted via wireless debugging on Android 11+. Only works via USB.
- **MIUI install blocked** — `adb install` fails with `INSTALL_FAILED_USER_RESTRICTED` unless "Install via USB" is enabled in Developer Options. Fallback: push APK to `/sdcard/Download/` and install manually.

## Device Backup via ADB

`adb backup` is **deprecated on Android 12+** and requires on-device confirmation. It's unreliable. Use content providers instead.

### Contacts Backup
```bash
adb shell content query --uri content://com.android.contacts/contacts --projection display_name > contactos_lista.txt
```

### SMS Backup
```bash
adb shell content query --uri content://sms --projection address:body:date > sms_backup.txt
```

### File Metadata Backup
```bash
adb shell "ls -la /sdcard/DCIM/Camera/" > fotos_lista.txt
adb shell "ls -la /sdcard/Download/" > descargas_lista.txt
```

### App List Backup
```bash
adb shell pm list packages -3 | sed 's/package://g' | sort > apps_instaladas.txt
```

### Storage Info
```bash
adb shell "df -h /sdcard/"
```

**Note**: On MSYS/git-bash, `adb shell` commands with paths like `/sdcard/` get mangled by path conversion. Use quotes: `adb shell "df -h /sdcard/"` or `adb shell 'df -h /sdcard/'`.

### Full File Pull (photos, downloads)
```bash
# Pull all photos
adb pull /sdcard/DCIM/Camera/ ./POCO_Backup/Camera/

# Pull downloads
adb pull /sdcard/Download/ ./POCO_Backup/Download/
```

## Device Info Extraction
```bash
adb devices -l                          # Device list with details
adb shell getprop ro.product.model      # Model number
adb shell getprop ro.product.device     # Device codename
adb shell getprop ro.build.version.release  # Android version
adb shell getprop ro.build.display.id   # Build/MIUI version
```

## Fingerprint / Biometric Troubleshooting via ADB

Use this when the user says fingerprint/huella disappeared from Settings. Diagnose before assuming hardware failure:

```bash
SER='<device-or-mdns-serial>'
adb -s "$SER" shell '
  echo DEVICE; getprop ro.product.manufacturer; getprop ro.product.model; getprop ro.build.version.release; getprop ro.build.display.id
  echo FEATURES; cmd package list features | grep -Ei "finger|biometric|face" || true
  echo SETTINGS; settings list secure | grep -Ei "finger|biometric|face|lock" || true
  echo SERVICES; service list | grep -Ei "finger|biometric|face" || true
  echo FINGERPRINT; dumpsys fingerprint 2>/dev/null | head -80
  echo BIOMETRIC; dumpsys biometric 2>/dev/null | head -100
  echo POLICY; dumpsys device_policy | grep -Ei "finger|biometric|keyguard|disabled features|password" | head -80 || true
  echo RESTRICTIONS; dumpsys user | grep -Ei "no_config|finger|biometric|keyguard|restrictions" -A3 -B2 || true
'
```

Interpretation:
- `feature:android.hardware.fingerprint` + `service list` shows `fingerprint`/`biometric` + `dumpsys fingerprint` has sensor/provider = Android sees the sensor; likely Settings/menu/enrollment issue, not dead hardware.
- `count:0` or `fingerprint_enroll_status=0` = no fingerprints enrolled.
- Device policy/user restrictions can hide or disable biometric settings; check before changing anything.

Open the relevant Settings screen directly (works even when menus hide it):
```bash
adb -s "$SER" shell 'am start -a android.settings.FINGERPRINT_SETTINGS'
adb -s "$SER" shell 'am start -a android.settings.FINGERPRINT_ENROLL'
adb -s "$SER" shell 'am start -a android.settings.FINGERPRINT_SETUP'
```

If the phone is locked, wake it and inspect screenshot; ADB can open Settings but should not enter user PIN/pattern:
```bash
adb -s "$SER" shell input keyevent KEYCODE_WAKEUP
adb -s "$SER" exec-out screencap -p > ~/Desktop/phone_screen.png
```

## App Inventory & Optimization

### List Third-Party Apps
```bash
adb shell pm list packages -3 | sed 's/package://g' | sort
```
`-3` = third-party only (excludes system apps). This gives package names only.

### Categorization Framework
When optimizing a device, classify apps into:

| Category | Action | Examples |
|----------|--------|----------|
| **Essential** | Keep | WhatsApp, Telegram, Authenticator, user's own apps |
| **Banking/Payment** | Ask user | BNC, Banesco, Binance, PayPal |
| **Bloatware (safe to remove)** | Remove | MIUI Fashion Gallery, Google Magazines, ARCore |
| **Games** | Ask user | PvZ, Angry Birds, Warhammer |
| **Social/Media** | Ask user | TikTok, Netflix, Discord, Facebook |
| **Google apps** | Remove if unused | YouTube Music, YouTube Studio, Google Wallet, Translate |

### Common Xiaomi/MIUI Bloatware (safe to remove)
- `com.miui.android.fashiongallery` — MIUI Fashion Gallery
- `com.miui.mediaeditor` — MIUI Media Editor
- `com.duokan.phone.remotecontroller` — Mi Remote Control
- `cn.wps.xiaomi.abroad.lite` — WPS Office (Xiaomi version)

### Common Google Bloatware (safe to remove if unused)
- `com.google.android.apps.bard` — Google Bard AI
- `com.google.android.apps.magazines` — Google News/Magazines
- `com.google.android.apps.walletnfcrel` — Google Wallet (doesn't work in many countries)
- `com.google.android.apps.youtube.creator` — YouTube Studio
- `com.google.ar.core` / `com.google.ar.lens` — AR (heavy, rarely used)
- `com.google.android.safetycore` — Safety Core
- `com.google.android.contactkeys` — Contact Keys
- `com.google.android.googlequicksearchbox` — Google App/Discover (~175-237MB RAM, safe to disable)
- `com.google.android.apps.messaging` — Google Messages (~220-387MB RAM, massive hog on low-RAM devices)

### Restoring Removed Apps
If you accidentally remove a system app, restore it:
```bash
adb shell cmd package install-existing <package.name>
```
This works for apps uninstalled with `pm uninstall -k --user 0` (the `-k` flag keeps the data).

### Uninstall via ADB
```bash
# Uninstall (user-level, can be restored with reinstall)
adb uninstall <package.name>

# Disable (doesn't uninstall, just disables — safer for system apps)
adb shell pm disable-user --user 0 <package.name>

# Re-enable
adb shell pm enable <package.name>
```

**Prefer `disable-user` over `uninstall` for system apps** — disabling is reversible without needing to find the APK.

### Restrict Background Execution
For apps that shouldn't run in background (saves RAM and battery):
```bash
adb shell cmd appops set <package> RUN_IN_BACKGROUND deny
adb shell cmd appops set <package> RUN_ANY_IN_BACKGROUND deny
adb shell cmd appops set <package> WAKE_LOCK deny
adb shell am force-stop <package>
```
This is the most effective optimization for low-RAM devices. Apply to YouTube, Chrome, Google Messages, social media apps, etc.

### Disable Ad Tracking & Ad Services
```bash
# Disable personalized ad tracking
adb shell settings put secure limit_ad_tracking 1

# Disable Google ad services (Android 13+)
adb shell pm disable-user --user 0 com.google.android.adservices.api
adb shell pm disable-user --user 0 com.google.mainline.adservices
adb shell pm disable-user --user 0 com.google.mainline.telemetry
adb shell pm disable-user --user 0 com.google.android.sdksandbox
```

### Post-Debloat Verification
```bash
# Check remaining notifications for adware
adb shell dumpsys notification --noredact | grep "pkg=" | sort -u

# Check RAM improvement
adb shell cat /proc/meminfo | head -3

# Check storage freed
adb shell df -h /data
```

## Presenting Optimization to User

**Do NOT just delete apps.** Present a categorized list and let the user decide:
1. List all third-party apps
2. Categorize into Essential / Banking / Bloatware / Games / Social
3. Mark bloatware as "safe to remove"
4. Ask user which non-essential apps to keep
5. Batch uninstall/disable the agreed list

**User preference**: Present in a table format, in Spanish, grouped by category. Don't ask multiple-choice questions — give a clear list and let them say which to remove.

## ADB over USB Troubleshooting

If `adb devices` shows no devices:
1. Check USB cable (data cable, not charge-only)
2. Enable **USB Debugging** in Developer Options
3. On phone, pull down notification → select "File Transfer" mode (not "Charge only")
4. Accept the RSA key prompt on the phone ("Allow USB debugging?")
5. Try different USB port (some ports are charge-only)
6. Install OEM USB drivers (Xiaomi: Mi PC Suite or Universal ADB Driver)

### Windows-specific
- Device Manager → check for unknown devices with yellow warning
- Xiaomi devices may need Qualcomm HS-USB QDLoader 9008 driver for bootloader mode
- `adb kill-server && adb start-server` can fix stale connections
