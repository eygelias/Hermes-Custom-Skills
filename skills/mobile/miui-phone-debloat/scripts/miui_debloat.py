#!/usr/bin/env python3
"""
MIUI/Xiaomi Phone Debloat Script
Usage: python miui_debloat.py [--dry-run] [--system-only] [--third-party-only]

Removes bloatware from Xiaomi/POCO/Redmi phones via ADB.
Always does a backup first.
"""
import subprocess
import os
import sys
import time
from datetime import datetime

# Add platform-tools to PATH
os.environ["PATH"] = r"C:\Users\ELY\platform-tools" + ";" + os.environ.get("PATH", "")

def adb(cmd, device=None):
    """Execute ADB command."""
    args = ["adb"]
    if device:
        args.extend(["-s", device])
    args.extend(["shell", cmd])
    r = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def backup_data(device=None):
    """Create backup of contacts, SMS, and app list."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"Creating backup in {backup_dir}...")
    
    # Backup contacts
    out, _, _ = adb("content query --uri content://com.android.contacts/contacts --projection display_name", device)
    with open(f"{backup_dir}/contacts.txt", "w", encoding="utf-8") as f:
        f.write(out)
    print(f"  ✓ Contacts saved ({len(out.splitlines())} entries)")
    
    # Backup SMS
    out, _, _ = adb("content query --uri content://sms --projection address:body:date", device)
    with open(f"{backup_dir}/sms.txt", "w", encoding="utf-8") as f:
        f.write(out)
    print(f"  ✓ SMS saved ({len(out.splitlines())} entries)")
    
    # Backup app list
    out, _, _ = adb("pm list packages -3", device)
    with open(f"{backup_dir}/apps.txt", "w", encoding="utf-8") as f:
        f.write(out)
    print(f"  ✓ App list saved ({len(out.splitlines())} apps)")
    
    return backup_dir

# SAFE TO REMOVE - System bloatware
SYSTEM_BLOATWARE = [
    "com.miui.msa.global",           # MIUI Ads
    "com.miui.analytics",            # Telemetry
    "com.miui.bugreport",            # Bug reporting
    "com.miui.weather2",             # Weather
    "com.miui.compass",              # Compass
    "com.miui.fm",                   # FM Radio
    "com.miui.fmservice",            # FM Radio service
    "com.miui.cleaner",              # Cleaner
    "com.miui.yellowpage",           # Yellow pages
    "com.miui.touchassistant",       # Touch assistant
    "com.miui.extraphoto",           # Extra photos
    "com.miui.misound",              # Sound
    "com.miui.player",               # Music player
    "com.miui.videoplayer",          # Video player
    "com.miui.freeform",             # Floating windows
    "com.xiaomi.barrage",            # Barrage
    "com.xiaomi.discover",           # Discover
    "com.xiaomi.glgm",               # Games
    "com.xiaomi.midrop",             # Mi Drop
    "com.xiaomi.mipicks",            # App recommendations
    "com.xiaomi.payment",            # Payment
    "com.xiaomi.powerchecker",       # Power checker
    "com.xiaomi.simactivate.service", # SIM activation
    "com.mi.healthglobal",           # Health
    "com.milink.service",            # Mi Link
    "com.miui.cloudbackup",          # Cloud backup
    "com.miui.cloudservice",         # Cloud service
    "com.miui.micloudsync",          # Cloud sync
    "com.miui.hybrid",               # Hybrid apps
    "com.miui.hybrid.accessory",     # Hybrid accessory
    "com.miui.phrase",               # Phrases
    "com.miui.daemon",               # Daemon
    "com.miui.notification",         # Notifications
    "com.miui.wmsvc",                # WM service
    "com.miuix.editor",              # Editor
    "com.miui.audiomonitor",         # Audio monitor
]

# SAFE TO REMOVE - Google bloatware
GOOGLE_BLOATWARE = [
    "com.google.android.apps.googleassistant",    # Google Assistant
    "com.google.android.apps.turbo",              # Photo enhancer
    "com.google.android.apps.wellbeing",          # Digital Wellbeing
    "com.google.android.apps.subscriptions.red",  # Google One
    "com.google.android.apps.restore",            # Restore
    "com.google.android.gms.location.history",    # Location history
    "com.google.android.marvin.talkback",         # TalkBack
    "com.google.android.tts",                     # TTS
    "com.google.android.feedback",                # Feedback
    "com.google.android.printservice.recommendation",  # Print
    "com.google.android.projection.gearhead",     # Android Auto
]

# SAFE TO REMOVE - Facebook bloatware
FACEBOOK_BLOATWARE = [
    "com.facebook.appmanager",
    "com.facebook.services",
    "com.facebook.system",
]

# NEVER REMOVE
DO_NOT_REMOVE = [
    "com.miui.securitycenter",
    "com.miui.securityadd",
    "com.miui.guardprovider",
    "com.xiaomi.finddevice",
    "com.lbe.security.miui",
    "com.miui.home",
    "com.miui.packageinstaller",
    "com.xiaomi.market",
    "com.miui.core",
]

def remove_apps(apps, category, device=None, dry_run=False):
    """Remove a list of apps."""
    ok = 0
    fail = 0
    skip = 0
    
    for app in apps:
        if app in DO_NOT_REMOVE:
            print(f"  ⛔ {app} (NEVER REMOVE - skipping)")
            skip += 1
            continue
        
        if dry_run:
            print(f"  🔍 {app} (would remove)")
            ok += 1
            continue
        
        out, err, code = adb(f"pm uninstall -k --user 0 {app}", device)
        if code == 0:
            print(f"  ✅ {app}")
            ok += 1
        elif "not installed" in out or "not installed" in err:
            print(f"  ⏭️  {app} (not installed)")
            skip += 1
        else:
            print(f"  ❌ {app} -> {err or out}")
            fail += 1
        time.sleep(0.2)
    
    return ok, fail, skip

def main():
    dry_run = "--dry-run" in sys.argv
    system_only = "--system-only" in sys.argv
    third_party_only = "--third-party-only" in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE - No apps will be removed\n")
    
    # Check device connection
    out, _, code = adb("echo 'connected'")
    if "connected" not in out:
        print("❌ No device connected. Please connect via ADB first.")
        sys.exit(1)
    
    print("📱 Device connected\n")
    
    # Create backup
    if not dry_run:
        backup_dir = backup_data()
        print()
    
    # Remove system bloatware
    if not third_party_only:
        print("=" * 50)
        print("REMOVING SYSTEM BLOATWARE")
        print("=" * 50)
        ok, fail, skip = remove_apps(SYSTEM_BLOATWARE, "System", dry_run=dry_run)
        print(f"\n  System: {ok} removed, {fail} failed, {skip} skipped\n")
    
    # Remove Google bloatware
    if not third_party_only:
        print("=" * 50)
        print("REMOVING GOOGLE BLOATWARE")
        print("=" * 50)
        ok, fail, skip = remove_apps(GOOGLE_BLOATWARE, "Google", dry_run=dry_run)
        print(f"\n  Google: {ok} removed, {fail} failed, {skip} skipped\n")
    
    # Remove Facebook bloatware
    if not third_party_only:
        print("=" * 50)
        print("REMOVING FACEBOOK BLOATWARE")
        print("=" * 50)
        ok, fail, skip = remove_apps(FACEBOOK_BLOATWARE, "Facebook", dry_run=dry_run)
        print(f"\n  Facebook: {ok} removed, {fail} failed, {skip} skipped\n")
    
    print("=" * 50)
    print("✅ DEBLOAT COMPLETE")
    if not dry_run:
        print(f"Backup saved in: {backup_dir}")
    print("=" * 50)

if __name__ == "__main__":
    main()
