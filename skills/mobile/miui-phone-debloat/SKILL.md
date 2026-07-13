---
name: miui-phone-debloat
description: "Debloat and optimize Xiaomi/POCO/Redmi phones via ADB — safe removal lists, wireless debugging setup, bloatware research, and MIUI-specific pitfalls."
triggers:
  - "debloat xiaomi"
  - "remove bloatware miui"
  - "optimize poco phone"
  - "clean xiaomi phone"
  - "desinstalar apps sistema xiaomi"
  - "limpiar telefono xiaomi"
  - "remove miui bloatware"
---

# MIUI/Xiaomi Phone Debloating via ADB

## Prerequisites

### ADB Installation
If ADB is not installed on the PC:
```bash
# Download platform-tools
curl -L -o platform-tools.zip "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
unzip platform-tools.zip -d /c/Users/<user>/
# Add to PATH
export PATH="/c/Users/<user>/platform-tools:$PATH"
```

### Wireless Debugging Setup (Android 11+)
1. Enable **Developer Options** (tap Build Number 7 times)
2. Enable **USB Debugging** and **Wireless Debugging**
3. For pairing: use Python script (see pitfall below)
4. After pairing, connect with `adb connect <ip:port>`

## ⚠️ CRITICAL PITFALLS

### 1. ADB Pair on Windows - Cannot Pipe Input
**Problem:** `echo "code" | adb pair ip:port` fails on Windows.
**Solution:** Use a Python script:
```python
import subprocess, time
proc = subprocess.Popen(
    ["adb", "pair", "192.168.x.x:PORT"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
)
time.sleep(2)
proc.stdin.write("PAIRING_CODE\n")
proc.stdin.flush()
proc.stdin.close()
out = proc.communicate(timeout=15)[0]
print(out)
```

### 2. MIUI Install Restrictions
**Problem:** `INSTALL_FAILED_USER_RESTRICTED` when installing APKs via ADB.
**Cause:** MIUI has extra security even with "Install via USB" enabled.
**Solution:** 
- The phone will show a confirmation dialog - user MUST tap "Install"
- If dialog doesn't appear, check: Settings → Developer Options → Install via USB (must be ON)
- Also enable: Settings → Developer Options → USB debugging (Security settings)

### 3. Wireless ADB Port Changes After Reboot
After `adb reboot`, the wireless debugging port changes. Must reconnect with new IP:Port from phone settings.

## Safe Removal Lists

### 🚨 NEVER REMOVE (Causes Bootloop)
```
com.miui.securitycenter
com.miui.securityadd
com.miui.guardprovider
com.xiaomi.finddevice
com.lbe.security.miui
com.miui.home
com.miui.packageinstaller
com.xiaomi.market
com.miui.core
```

### ⚠️ RISKY (May Cause Issues)
```
com.xiaomi.joyose          # May cause overheating during gaming
com.miui.powerkeeper       # Debated - can worsen battery
com.miui.miwallpaper       # Crashes Themes app
com.xiaomi.micloud.sdk     # Breaks Gallery cloud features
com.xiaomi.xmsf            # Breaks internet in Xiaomi apps
com.xiaomi.xmsfkeeper      # Breaks internet in Xiaomi apps
```

### ✅ SAFE TO REMOVE (System Bloatware)
```
com.miui.msa.global        # MIUI Ads (HIGH PRIORITY to remove)
com.miui.analytics         # Telemetry/spying
com.miui.bugreport         # Bug reporting
com.miui.weather2          # Weather app
com.miui.compass           # Compass
com.miui.fm                # FM Radio
com.miui.fmservice         # FM Radio service
com.miui.cleaner           # Junk cleaner
com.miui.yellowpage        # Yellow pages
com.miui.touchassistant    # Touch assistant
com.miui.extraphoto        # Extra photo features
com.miui.misound           # Sound enhancer
com.miui.player            # Music player
com.miui.videoplayer       # Video player
com.miui.freeform          # Floating windows
com.xiaomi.barrage         # Barrage notifications
com.xiaomi.discover        # Discover apps
com.xiaomi.glgm            # Games
com.xiaomi.midrop          # Mi Drop
com.xiaomi.mipicks         # App recommendations
com.xiaomi.payment         # Xiaomi payment (not in Venezuela)
com.xiaomi.powerchecker    # Power checker
com.xiaomi.simactivate.service  # SIM activation
com.mi.healthglobal        # Mi Health
com.milink.service         # Mi Link
com.miui.cloudbackup       # Cloud backup
com.miui.cloudservice      # Cloud service
com.miui.micloudsync       # Cloud sync
com.miui.hybrid            # Hybrid apps
com.miui.hybrid.accessory  # Hybrid accessory
com.miui.phrase            # Phrase suggestions
com.miui.daemon            # Daemon
com.miui.notification      # Notification manager
com.miui.wmsvc             # WM service
com.miuix.editor           # Editor
com.miui.audiomonitor      # Audio monitor
```

### ✅ SAFE TO REMOVE (Google Bloatware)
```
com.google.android.apps.googleassistant   # Google Assistant
com.google.android.apps.turbo             # Photo enhancer
com.google.android.apps.wellbeing         # Digital Wellbeing
com.google.android.apps.subscriptions.red # Google One
com.google.android.apps.restore           # Google Restore
com.google.android.gms.location.history   # Location History
com.google.android.marvin.talkback        # TalkBack
com.google.android.tts                    # Text-to-speech
com.google.android.feedback               # Feedback
com.google.android.printservice.recommendation  # Print service
com.google.android.projection.gearhead    # Android Auto
```

### ✅ SAFE TO REMOVE (Facebook Bloatware)
```
com.facebook.appmanager    # Facebook App Manager
com.facebook.services      # Facebook Services
com.facebook.system        # Facebook System
```

## Removal Commands

### Method 1: Disable (Reversible)
```bash
adb shell pm disable-user --user 0 <package.name>
```

### Method 2: Uninstall for User (Recommended)
```bash
adb shell pm uninstall -k --user 0 <package.name>
```
**Note:** `-k` keeps data. Apps remain in system partition but are removed for the user. Can be restored with factory reset.

### Method 3: Full Uninstall (Requires Root)
```bash
adb shell pm uninstall <package.name>
```

## Backup Before Removing

### Contacts
```bash
adb shell content query --uri content://com.android.contacts/contacts --projection display_name > contacts.txt
```

### SMS
```bash
adb shell content query --uri content://sms --projection address:body:date > sms.txt
```

### App List
```bash
adb shell pm list packages -3 | sed 's/package://g' | sort > apps.txt
```

### Storage Info
```bash
adb shell df -h /sdcard/
```

## Restoring Accidentally Removed Apps

If a needed app was removed, restore it without factory reset:
```bash
adb shell cmd package install-existing <package.name>
```

### Common Accidental Removals
- `com.miui.mediaeditor` — Breaks screenshot editing (floating thumbnail)
- `com.miui.screenshot` — Breaks screenshot capture
- `com.mi.android.globalminusscreen` — News feed (may want to remove anyway)

## Home Screen News Feed

The MIUI news feed (swipe right on home screen) is `com.mi.android.globalminusscreen`. Remove with:
```bash
adb shell pm uninstall -k --user 0 com.mi.android.globalminusscreen
# Also disable launcher feed settings
adb shell settings put secure launcher_extra_feed_disable 1
adb shell settings put secure launcher_feed_enable 0
adb shell settings put secure minus_screen_enable 0
```

## Gallery & Photo Editor Notes

### Samsung Gallery on Non-Samsung Phones
**Does NOT work.** Samsung Gallery requires Samsung-specific frameworks and hardware. Will crash or not install.

### Xiaomi Gallery Editor (com.miui.mediaeditor)
- AI features (erase, expand, enhance) are **cloud-based** (not on-device)
- Available on: Redmi Note 14 series, POCO X7 Pro, newer devices
- **SDK Requirements:**
  - v2.3.x requires Android 12L+ (SDK 32) - WON'T work on Android 12
  - v2.0.x requires Android 12+ (SDK 31) - Should work
  - v1.10.x requires Android 11+ (SDK 30) - Works on older devices
- **APK Sources:** APKMirror, Aptoide (search for `com.miui.mediaeditor`)

### Setting Default Photo Viewer
After removing MIUI Gallery, Android will prompt to choose default app when opening photos. Select Google Photos and choose "Always".

## Useful Commands

```bash
# List all third-party apps
adb shell pm list packages -3

# List all system apps
adb shell pm list packages -s

# Check device info
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release

# Check storage
adb shell df -h /sdcard/

# Reboot device
adb reboot

# Check connected devices
adb devices -l
```
