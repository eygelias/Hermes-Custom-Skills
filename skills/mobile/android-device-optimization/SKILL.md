---
name: android-device-optimization
description: "ADB wireless debugging, Xiaomi/MIUI debloat, battery optimization, system app replacement. Works on POCO, Redmi, Xiaomi devices."
tags: [android, adb, debloat, xiaomi, miui, poco, battery, optimization]
triggers:
  - debloat Android phone
  - remove Xiaomi bloatware
  - optimize Android battery
  - ADB wireless debugging
  - MIUI system apps safe to remove
  - replace MIUI apps with Google
---

# Android Device Optimization

## ⚠️ Critical Pitfalls

### Batch ADB Operations — Use Bash, Not Python Subprocess

When running many ADB commands (debloat, batch uninstall, background restriction), **always use bash loops via `terminal()`**, NOT Python subprocess via `execute_code()`.

**Why:** Python subprocess calls via execute_code each spawn a new adb client. After ~20-30 commands, the adb daemon restarts and loses the device connection (`device not found`). Bash loops keep a single adb client session alive.

```bash
# ✅ CORRECT — bash loop via terminal()
export PATH="/c/Users/ELY/platform-tools:$PATH"
DEV="192.168.100.229:42873"
adb connect "$DEV" > /dev/null 2>&1
for pkg in com.app.one com.app.two com.app.three; do
  result=$(adb -s "$DEV" shell pm uninstall -k --user 0 "$pkg" 2>&1)
  echo "$pkg -> $result"
done
```

```python
# ❌ WRONG — Python subprocess via execute_code
# Will lose connection after ~20-30 packages
import subprocess
for pkg in packages:
    subprocess.run(["adb", "-s", DEV, "shell", "pm", "uninstall", ...])
```

### Wireless Debugging — Settings Commands Fail

On Android 11+ via wireless debugging, `settings put global/secure/system` commands fail with `SecurityException: Permission denial: writing to settings requires android.permission.WRITE_SECURE_SETTINGS`. This is a **wireless debugging limitation**, not a bug. These commands only work via USB cable.

Affected: animation scales, wifi_scan_always_enabled, bluetooth_always_on, mobile_data_always_on, miui_telemetry_mode, screen_off_timeout, etc.

**Workaround:** Tell the user to change these manually in Settings, or connect via USB.

### MIUI APK Installation Blocked

`adb install` fails on MIUI with `INSTALL_FAILED_USER_RESTRICTED` unless:
- **Settings → Developer Options → Install via USB** is enabled
- **Settings → Developer Options → USB debugging (Security settings)** is enabled

If user can't enable these, push APKs to `/sdcard/Download/` instead:
```bash
adb -s "$DEV" push app.apk /sdcard/Download/app.apk
```
Then user installs manually via file manager.

## ADB Wireless Debugging Setup (Windows)

### Initial Pairing — Critical Windows Pitfall

`adb pair` does NOT accept piped input on Windows. The following approaches FAIL:
```bash
# ❌ FAILS — pipe doesn't work
echo "123456" | adb pair 192.168.1.1:12345
printf "123456\n" | adb pair 192.168.1.1:12345
adb pair 192.168.1.1:12345 <<< "123456"
```

**Working approach — Python subprocess:**
```python
import subprocess, time
proc = subprocess.Popen(
    ["adb", "pair", "192.168.1.1:12345"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
)
time.sleep(2)
proc.stdin.write("123456\n")
proc.stdin.flush()
proc.stdin.close()
out = proc.communicate(timeout=15)[0]
print(out)  # "Successfully paired to ..."
```

**Also works — Background PTY + submit:**
1. `terminal(background=true, pty=true, command="adb pair IP:PORT")`
2. `process(action='poll')` — wait for "Enter pairing code:"
3. `process(action='submit', data="CODE")`
4. `process(action='wait', timeout=10)`

### Pairing vs Connecting — Two Different Steps

| Step | Command | When |
|------|---------|------|
| **Pair** | `adb pair IP:PORT_FROM_PAIRING_DIALOG` | First time only, uses 6-digit code |
| **Connect** | `adb connect IP:PORT_FROM_MAIN_SCREEN` | Every time after reboot |

The pairing port (from "Link with pairing code") is DIFFERENT from the main wireless debugging port. After pairing, use the main IP:Port shown on the wireless debugging screen.

### After Reboot

Wireless ADB port changes after every reboot. Must reconnect with new port:
```bash
adb connect NEW_IP:NEW_PORT
```

## Xiaomi/MIUI Debloat

### 🚨 NEVER REMOVE — Will Cause Bootloop

| Package | App |
|---------|-----|
| `com.miui.securitycenter` | Security Center |
| `com.miui.securityadd` | Security Add-on |
| `com.miui.guardprovider` | Guard Provider |
| `com.xiaomi.finddevice` | Find Device |
| `com.lbe.security.miui` | Permission Manager |
| `com.miui.home` | System Launcher |
| `com.miui.packageinstaller` | Package Installer |
| `com.xiaomi.account` | Xiaomi Account |
| `com.xiaomi.market` | App Store |
| `com.miui.core` | Core System (breaks Settings search) |

### ⚠️ RISKY — May Cause Issues

| Package | Risk |
|---------|------|
| `com.xiaomi.joyose` | Overheating during gaming |
| `com.miui.powerkeeper` | Safe to disable (`pm disable-user --user 0`) — frees ~97MB RAM. Debated for battery but confirmed no issues after disabling on Redmi 9C. |
| `com.miui.miwallpaper` | Crashes Themes app |
| `com.xiaomi.micloud.sdk` | Breaks Gallery cloud features |
| `com.xiaomi.xmsf` | Breaks internet in Xiaomi apps |
| `com.xiaomi.xmsfkeeper` | Breaks internet in Xiaomi apps |

### ✅ Safe to Remove — System Bloatware

```bash
# Use pm uninstall -k --user 0 (removes for user, restores on factory reset)
# NOT pm uninstall (permanent, risky)

# Xiaomi/MIUI bloatware
adb shell pm uninstall -k --user 0 com.miui.msa.global      # MIUI Ads
adb shell pm uninstall -k --user 0 com.miui.analytics        # Telemetry
adb shell pm uninstall -k --user 0 com.miui.bugreport        # Bug reporter
adb shell pm uninstall -k --user 0 com.miui.weather2         # Weather
adb shell pm uninstall -k --user 0 com.miui.compass           # Compass
adb shell pm uninstall -k --user 0 com.miui.fm                # FM Radio
adb shell pm uninstall -k --user 0 com.miui.fmservice         # FM Radio service
adb shell pm uninstall -k --user 0 com.miui.cleaner           # Cleaner
adb shell pm uninstall -k --user 0 com.miui.yellowpage        # Yellow pages
adb shell pm uninstall -k --user 0 com.miui.touchassistant    # Touch assistant
adb shell pm uninstall -k --user 0 com.miui.extraphoto        # Extra photo
adb shell pm uninstall -k --user 0 com.miui.misound           # Sound enhancer
adb shell pm uninstall -k --user 0 com.miui.player            # Music player
adb shell pm uninstall -k --user 0 com.miui.videoplayer       # Video player
adb shell pm uninstall -k --user 0 com.miui.freeform          # Floating windows
adb shell pm uninstall -k --user 0 com.xiaomi.barrage         # Barrage notifications
adb shell pm uninstall -k --user 0 com.xiaomi.discover         # Discover apps
adb shell pm uninstall -k --user 0 com.xiaomi.glgm            # Games
adb shell pm uninstall -k --user 0 com.xiaomi.midrop          # Mi Drop
adb shell pm uninstall -k --user 0 com.xiaomi.mipicks         # Mi Picks (may fail — protected)
adb shell pm uninstall -k --user 0 com.xiaomi.payment         # Xiaomi Pay
adb shell pm uninstall -k --user 0 com.xiaomi.powerchecker    # Power checker
adb shell pm uninstall -k --user 0 com.xiaomi.simactivate.service
adb shell pm uninstall -k --user 0 com.mi.healthglobal        # Mi Health
adb shell pm uninstall -k --user 0 com.milink.service         # Mi Link
adb shell pm uninstall -k --user 0 com.miui.cloudbackup       # Cloud backup
adb shell pm uninstall -k --user 0 com.miui.cloudservice      # Cloud service
adb shell pm uninstall -k --user 0 com.miui.micloudsync       # Cloud sync
adb shell pm uninstall -k --user 0 com.miui.hybrid            # Hybrid apps
adb shell pm uninstall -k --user 0 com.miui.hybrid.accessory
adb shell pm uninstall -k --user 0 com.miui.phrase            # Phrase suggestions
adb shell pm uninstall -k --user 0 com.miui.daemon            # Daemon
adb shell pm uninstall -k --user 0 com.miui.notification      # Notification manager
adb shell pm uninstall -k --user 0 com.miui.wmsvc             # WM service
adb shell pm uninstall -k --user 0 com.miuix.editor           # Editor
adb shell pm uninstall -k --user 0 com.miui.audiomonitor      # Audio monitor

# Google bloatware
adb shell pm uninstall -k --user 0 com.google.android.apps.googleassistant
adb shell pm uninstall -k --user 0 com.google.android.apps.turbo
adb shell pm uninstall -k --user 0 com.google.android.apps.wellbeing
adb shell pm uninstall -k --user 0 com.google.android.apps.subscriptions.red
adb shell pm uninstall -k --user 0 com.google.android.apps.restore
adb shell pm uninstall -k --user 0 com.google.android.gms.location.history
adb shell pm uninstall -k --user 0 com.google.android.marvin.talkback
adb shell pm uninstall -k --user 0 com.google.android.tts
adb shell pm uninstall -k --user 0 com.google.android.feedback
adb shell pm uninstall -k --user 0 com.google.android.printservice.recommendation
adb shell pm uninstall -k --user 0 com.google.android.projection.gearhead

# Facebook bloatware (background battery drain)
adb shell pm uninstall -k --user 0 com.facebook.appmanager
adb shell pm uninstall -k --user 0 com.facebook.services
adb shell pm uninstall -k --user 0 com.facebook.system
```

### MIUI Gallery Removal

Safe to remove both:
```bash
adb shell pm uninstall -k --user 0 com.miui.gallery         # MIUI Gallery
adb shell pm uninstall -k --user 0 com.miui.mediaeditor      # Gallery Editor
```
Google Photos becomes default automatically after removal.

**Note:** Xiaomi Gallery Editor AI features (erase, expand) are cloud-based but require SDK 32+ (Android 12L). Won't work on Android 12 devices even if APK is installed.

## Battery Optimization

### Identify Top Consumers
```bash
adb shell dumpsys batterystats --charged | grep -A 30 "Estimated power use"
# UIDs like u0a262 = package UID 10262
adb shell pm list packages -U | grep "uid:10262"
```

### Restrict Background for Heavy Apps (Full Approach)
```bash
# Deny all background execution
adb shell cmd appops set <package> RUN_IN_BACKGROUND deny
adb shell cmd appops set <package> RUN_ANY_IN_BACKGROUND deny
adb shell cmd appops set <package> WAKE_LOCK deny

# Force stop to immediately free RAM
adb shell am force-stop <package>
```

**Apply to all non-essential apps that shouldn't run in background:** YouTube, Chrome, Google Messages, Google App, Maps, Calendar, Gmail, Facebook Lite, TikTok, Google Assistant, Talkback, TTS, AR Lens, etc.

### Disable Heavy System Apps (Without Removing)
```bash
# Disables the app — reversible with `pm enable`
adb shell pm disable-user --user 0 <package>
```
**Confirmed safe to disable:**
- `com.google.android.googlequicksearchbox` — Google App/Discover (~175MB RAM)
- `com.miui.powerkeeper` — Power keeper (~97MB RAM)
- `com.google.android.cellbroadcastreceiver` — Emergency alerts (~75MB RAM)

### System Settings for Battery Savings
```bash
# Animations
adb shell settings put global window_animation_scale 0.5
adb shell settings put global transition_animation_scale 0.5
adb shell settings put global animator_duration_scale 0.5

# Location off
adb shell settings put secure location_mode 0

# Reduce brightness
adb shell settings put system screen_brightness 100

# Disable haptic feedback
adb shell settings put system haptic_feedback_enabled 0

# Disable auto-sync
adb shell settings put global auto_sync 0

# Disable scanning
adb shell settings put global wifi_scan_always_enabled 0
adb shell settings put global bluetooth_always_on 0
adb shell settings put global ble_scan_always_enabled 0

# Disable NFC
adb shell settings put global nfc_on 0

# Disable mobile data always-on
adb shell settings put global mobile_data_always_on 0

# Screen timeout 1 min
adb shell settings put system screen_off_timeout 60000

# Disable auto-updates
adb shell settings put global auto_update 0

# Disable MIUI telemetry
adb shell settings put secure miui_telemetry_mode 0
adb shell settings put secure upload_log_pref 0

# Disable ADB verification (helps with install speed)
adb shell settings put global verifier_verify_adb_installs 0
```

## Install APKs via ADB on MIUI

MIUI requires user confirmation on device even with ADB:
```bash
adb install -r <apk>  # Phone shows dialog, user must tap Install
```

If dialog doesn't appear:
```bash
adb shell settings put global verifier_verify_adb_installs 0
adb shell settings put secure install_non_market_apps 1
```

**Must have enabled:**
- Settings → Developer Options → Install via USB ✅
- Settings → Developer Options → USB debugging (Security settings) ✅

## Low-RAM Device Optimization (≤2GB RAM)

Devices with ≤2GB RAM need aggressive optimization. The biggest RAM hogs are usually:

1. **Google App/Discover** (~175MB) — disable with `pm disable-user`
2. **Google Messages RCS** (~387MB total) — if user uses MIUI SMS, disable
3. **Chrome** (~112MB) — suggest lighter browser (Samsung Internet, Firefox Lite)
4. **YouTube** (~128MB running in background) — restrict background
5. **Powerkeeper** (~97MB) — safe to disable
6. **Google Play Services** (~250MB combined) — can't remove, but can restrict

### Step-by-step for low-RAM devices:

```bash
DEV="<ip:port>"
adb connect "$DEV" > /dev/null 2>&1

# 1. Disable heavy system apps (reversible with `pm enable`)
for pkg in com.google.android.googlequicksearchbox com.miui.powerkeeper com.google.android.cellbroadcastreceiver; do
  adb -s "$DEV" shell pm disable-user --user 0 "$pkg"
done

# 2. Remove unnecessary services
for pkg in com.google.android.setupwizard com.google.android.partnersetup com.xiaomi.mi_connect_service; do
  adb -s "$DEV" shell pm uninstall -k --user 0 "$pkg"
done

# 3. Restrict ALL non-essential apps from running in background
#    This is the BIGGEST win for low-RAM devices
NON_ESSENTIAL=(
  com.google.android.apps.messaging com.google.android.youtube
  com.android.chrome com.google.android.apps.maps
  com.google.android.calendar com.google.android.gm
  com.facebook.lite com.zhiliaoapp.musically.go
  com.google.android.apps.googleassistant com.google.android.marvin.talkback
  com.google.android.tts com.google.ar.lens
)
for pkg in "${NON_ESSENTIAL[@]}"; do
  adb -s "$DEV" shell cmd appops set "$pkg" RUN_IN_BACKGROUND deny
  adb -s "$DEV" shell cmd appops set "$pkg" RUN_ANY_IN_BACKGROUND deny
  adb -s "$DEV" shell cmd appops set "$pkg" WAKE_LOCK deny
  adb -s "$DEV" shell am force-stop "$pkg"
done

# 4. Clear cache
adb -s "$DEV" shell pm trim-caches 100M
```

### Check RAM results:
```bash
adb -s "$DEV" shell cat /proc/meminfo | head -3
adb -s "$DEV" shell dumpsys meminfo | grep -E "^\s+[0-9,]+K:" | head -15
```

### Re-enabling a disabled app:
```bash
adb -s "$DEV" shell pm enable <package>
```

## Replacing MIUI Apps with Google

Safe replacements (install Google version, MIUI version auto-deactivates):

| MIUI | Google | Package |
|------|--------|---------|
| Gallery | Google Photos | `com.google.android.apps.photos` |
| Contacts | Google Contacts | `com.google.android.contacts` |
| Messages | Google Messages | `com.google.android.apps.messaging` |
| Calculator | Google Calculator | `com.google.android.calculator` |
| Files | Google Files | `com.google.android.apps.nbu.files` |
| Clock | Google Clock | `com.google.android.deskclock` |
| Keyboard | Gboard | `com.google.android.inputmethod.latin` |

**Cannot replace** (system components): Phone/Dialer, SMS service, System UI, Launcher (use third-party launcher but don't remove MIUI Home).

## Restoring Accidentally Removed Apps

If you accidentally uninstall a system app that's needed, restore it:
```bash
# Restore system app for current user
adb shell cmd package install-existing <package.name>
```

### Apps That Are Easy to Accidentally Remove
- `com.miui.mediaeditor` — Gallery Editor (needed for screenshot editing)
- `com.miui.screenshot` — Screenshot tool (needed for screenshot capture + edit)
- `com.mi.android.globalminusscreen` — News feed on home screen swipe

**Warning:** Removing `com.miui.mediaeditor` breaks the screenshot editing feature (floating thumbnail with edit/send buttons after capture). If removed, restore with:
```bash
adb shell cmd package install-existing com.miui.mediaeditor
```

## Disabling Home Screen News Feed (MIUI Minus Screen)

The news feed that appears when swiping right on the home screen:
```bash
# Remove MIUI news feed
adb shell pm uninstall -k --user 0 com.mi.android.globalminusscreen

# Also disable Google Discover feed in launcher
adb shell settings put secure launcher_extra_feed_disable 1
adb shell settings put secure launcher_feed_enable 0
adb shell settings put secure minus_screen_enable 0
```

## Downloading APKs via Aptoide API

When APKMirror is hard to navigate, use Aptoide's API for direct download links:
```bash
# Get APK metadata and download URL
curl -s "https://ws75.aptoide.com/api/7/app/getMeta?package_name=<package.name>" | grep -o '"path":"[^"]*"'

# Get multiple versions
curl -s "https://ws75.aptoide.com/api/7/app/getVersions?package_name=<package.name>&limit=10" | grep -E "vername|sdkmin|path"
```

## Installing Replacement Apps via Aptoide + ADB Push

When direct `adb install` is blocked by MIUI, download APKs from Aptoide API and push to phone:

```bash
# 1. Get download URL from Aptoide API
curl -s "https://ws75.aptoide.com/api/7/app/getMeta?package_name=<package>" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(d['data']['file']['path'])
"

# 2. Download APK
curl -L -o app.apk "<url>"

# 3. Push to phone (if install is blocked)
adb -s "$DEV" push app.apk /sdcard/Download/app.apk
# User installs manually from file manager

# 4. OR install directly (requires "Install via USB" enabled)
adb -s "$DEV" install -r app.apk
```

## Useful Diagnostic Commands

```bash
# Battery info
adb shell dumpsys battery

# Top battery consumers
adb shell dumpsys batterystats --charged

# Storage usage
adb shell df -h /sdcard/

# List third-party apps
adb shell pm list packages -3

# List system apps
adb shell pm list packages -s

# Check app UID
adb shell pm list packages -U | grep <package>

# Device info
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
```
