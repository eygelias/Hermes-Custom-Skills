---
name: android-adb-debloat
description: Connect to Android via ADB (USB or wireless), list/categorize apps, research safe-to-remove bloatware, and debloat without bricking. Covers MIUI/Xiaomi/POCO and TECNO/Transsion/HiOS.
tags: [android, adb, debloat, bloatware, xiaomi, miui, poco, tecno, transsion, hios, optimization]
---

# Android ADB Debloat

Remove bloatware from Android phones safely via ADB. Covers wireless ADB pairing, app inventory, risk research, and safe removal.

## Prerequisites

- ADB platform-tools installed (download from Google if missing)
- Phone connected via USB cable **or** WiFi (wireless debugging)
- Developer options + USB debugging enabled on phone

## Step 1: Connect via Wireless ADB

Wireless ADB on Android 11+ requires **pairing first**, then connecting:

```
# 1. Phone: Settings > Developer options > Wireless debugging > Enable
# 2. Phone: Tap "Pair device with pairing code" — note the IP:PORT and 6-digit code
# 3. PC: Pair (code changes fast, must be quick)
adb pair <IP>:<PAIR_PORT>
# Enter the 6-digit code when prompted

# 4. Phone: Note the main IP:PORT from the Wireless debugging screen (different from pairing port)
# 5. PC: Connect
adb connect <IP>:<MAIN_PORT>
```

### PITFALL: `adb pair` hangs with piped input on Windows
On Windows (git-bash/MSYS), `adb pair` does not accept piped stdin or heredocs reliably. Use a Python script with `subprocess.Popen`:

```python
import subprocess, time
proc = subprocess.Popen(
    ["adb", "pair", "<IP>:<PORT>"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
)
time.sleep(2)
proc.stdin.write("<CODE>\n")
proc.stdin.flush()
proc.stdin.close()
out = proc.communicate(timeout=15)[0]
print(out)
```

### PITFALL: Wireless ADB drops after reboot
After `adb reboot`, the wireless debug port changes. Re-pair or ask user for the new IP:PORT from the phone screen.

## Step 2: Inventory Apps

```bash
# Third-party apps (user-installed)
adb shell pm list packages -3 | sed 's/package://' | sort

# System apps
adb shell pm list packages -s | sed 's/package://' | sort

# Storage usage
adb shell df -h /sdcard/
```

## Step 3: Research BEFORE Removing

**CRITICAL USER PREFERENCE**: Always research which apps are safe to remove before acting. The user explicitly said: *"No borres a lo loco, primero investiga si al borrar algo puede romper o buguear el sistema."*

Search the web for:
- "[Device model] safe to remove system apps"
- "MIUI bloatware removal list safe"
- Check GitHub gists (e.g., mcxiaoke/ade05718f590bcd574b807c4706a00b1) and Reddit r/PocoPhones

Present results in a table with: App name, What it does, Risk level.

## Step 4: Removal Methods

### Pre-removal: Force-stop (breaks stuck overlays/adware)
```bash
# Force-stop adware BEFORE uninstall to break stuck fullscreen overlays
adb shell am force-stop <package.name>
```

### Method A: Disable (reversible)
```bash
adb shell pm disable-user --user 0 <package.name>
```
App becomes invisible but files remain. Can re-enable later.

### Method B: Uninstall for user (effectively removed, factory reset restores)
```bash
# For system apps (preserves data partition)
adb shell pm uninstall -k --user 0 <package.name>

# For third-party apps
adb shell pm uninstall --user 0 <package.name>
```

**Always use Method B for actual removal.** Method A alone doesn't free space or hide apps from launcher on all MIUI versions.

### Re-enable / Restore
```bash
# Re-enable a disabled app
adb shell pm enable --user 0 <package.name>

# Restore uninstalled system app (needs the package still in system partition)
adb shell cmd package install-existing <package.name>
```

## Xiaomi/MIUI/POCO Critical Knowledge

### NEVER REMOVE (causes bootloop)
- `com.miui.securitycenter` — Security Center (core)
- `com.miui.securityadd` — Security add-on
- `com.miui.guardprovider` — Security component
- `com.xiaomi.finddevice` — Find Device
- `com.lbe.security.miui` — Permission Manager
- `com.miui.home` — System Launcher
- `com.miui.packageinstaller` — Package Installer
- `com.xiaomi.account` — Xiaomi Account
- `com.xiaomi.market` — App Store
- `com.miui.core` — Core framework (breaks Settings search)

### RISKY (may cause issues)
- `com.xiaomi.joyose` — Removing causes overheating during gaming
- `com.miui.powerkeeper` — Debated; may worsen battery life
- `com.miui.miwallpaper` — Crashes Themes app
- `com.xiaomi.micloud.sdk` — Breaks Gallery cloud features
- `com.xiaomi.xmsf` / `com.xiaomi.xmsfkeeper` — Breaks internet in Xiaomi apps
- `com.miui.personalassistant` — May break widget picker

### Safe Bloatware List (MIUI)
Anuncios/Telemetry: `com.miui.msa.global`, `com.miui.analytics`, `com.xiaomi.joyose` (unless gaming)
Apps innecesarias: `com.miui.weather2`, `com.miui.compass`, `com.miui.fm`, `com.miui.fmservice`, `com.miui.cleaner`, `com.miui.yellowpage`, `com.miui.touchassistant`
Media: `com.miui.extraphoto`, `com.miui.misound`, `com.miui.player`, `com.miui.videoplayer`
Servicios: `com.miui.cloudbackup`, `com.miui.cloudservice`, `com.miui.micloudsync`, `com.miui.hybrid`, `com.miui.hybrid.accessory`, `com.miui.phrase`, `com.miui.daemon`, `com.miui.notification`, `com.miui.wmsvc`, `com.miuix.editor`, `com.miui.audiomonitor`, `com.miui.freeform`, `com.miui.bugreport`
Xiaomi: `com.xiaomi.barrage`, `com.xiaomi.discover`, `com.xiaomi.glgm`, `com.xiaomi.midrop`, `com.xiaomi.mipicks` (protected, may fail), `com.xiaomi.payment`, `com.xiaomi.powerchecker`, `com.xiaomi.simactivate.service`, `com.mi.healthglobal`, `com.milink.service`

### Safe Google Bloatware
`com.google.android.apps.googleassistant`, `com.google.android.apps.turbo`, `com.google.android.apps.wellbeing`, `com.google.android.apps.subscriptions.red`, `com.google.android.apps.restore`, `com.google.android.gms.location.history`, `com.google.android.marvin.talkback`, `com.google.android.tts`, `com.google.android.feedback`, `com.google.android.printservice.recommendation`, `com.google.android.projection.gearhead`

### Facebook System Apps
`com.facebook.appmanager`, `com.facebook.services`, `com.facebook.system` — Run silently, consume RAM/battery. Safe to remove if user doesn't use Facebook app.

## Step 5: Verify After Removal

```bash
# Check phone still responds
adb shell echo "OK"

# List remaining third-party apps
adb shell pm list packages -3

# Count remaining
adb shell pm list packages -3 | wc -l
```

## Bulk Removal Script Pattern

Use Python with subprocess for reliable batch operations:

```python
import subprocess, os, time
os.environ["PATH"] = r"C:\Users\ELY\platform-tools" + ";" + os.environ.get("PATH","")

def adb(cmd):
    r = subprocess.run(["adb", "shell", cmd], capture_output=True, text=True, timeout=15)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

apps = ["com.example.app1", "com.example.app2"]
for app in apps:
    out, err, code = adb(f"pm uninstall -k --user 0 {app}")
    status = "✅" if code == 0 else "❌"
    print(f"{status} {app}")
    time.sleep(0.2)
```

## TECNO / Transsion / HiOS Devices

Full debloat list in `references/tecno-transsion-debloat.md`. Key points:

**CRITICAL — NEVER REMOVE on TECNO:**
- `tech.palm.id` — **disables the Settings app**, phone becomes unusable
- `com.scorpio.securitycom` — TECNO security framework, protected from uninstall AND disable. Restrict background instead.
- `com.skyroam.silverhelper` — causes permissions to keep resetting

**Screen blackout from adware**: TECNO phones ship with 20+ adware apps that create fullscreen overlays. When user dismisses an ad mid-animation, the overlay gets stuck → screen goes black, requires reboot. **Fix**: force-stop all adware apps first (`am force-stop <pkg>`), then uninstall. The force-stop breaks stuck overlays immediately.

**TECNO/Transsion safe-to-remove summary**: 31+ system apps including Phone Master, Phone Manager, AI Assistant, Magazine Service, Tecno Spot, Carlcare, BatteryLab, Hamal, etc. See reference file for complete list.

## Pitfalls

- `pm clear --cache-only` is extremely slow via ADB (~1-2 seconds per app). Clearing cache for 100+ apps will timeout. Recommend user clear cache from Settings > Storage instead.
- Some packages return `DELETE_FAILED_INTERNAL_ERROR` — these are protected by OEM security. Try `pm disable-user` instead, or restrict background with `cmd appops`.
- `com.google.android.safetycore` is protected on some Android 13 builds — cannot uninstall or disable.
- After debloat, check remaining notifications: `adb shell dumpsys notification --noredact | grep "pkg="` to verify no adware remains active.

## Key Workflow Principles

1. **Inventory first** — list all apps, categorize (system vs third-party, essential vs bloat)
2. **Research** — web search for device-specific safe lists; never guess
3. **Present to user** — show what each app does, let user decide what to keep
4. **Remove in bulk** — use Python script for reliability
5. **Verify** — reboot and confirm phone still works
6. **Document** — save what was removed for future reference
