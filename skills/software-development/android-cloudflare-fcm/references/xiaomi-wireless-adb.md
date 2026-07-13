# Xiaomi/POCO Wireless ADB Setup

## Enable Developer Options
1. Settings → About Phone → tap "MIUI Version" 7 times
2. Settings → Additional Settings → Developer Options

## Enable Wireless Debugging (Android 11+)
1. Developer Options → "Wireless debugging" → enable
2. Tap "Wireless debugging" to enter submenu
3. Tap "Pair device with pairing code"
4. Note the **IP:port** and **6-digit code**

## ADB Commands

```bash
# Pair (use the pairing IP:port and code)
adb pair <ip:pairing_port>
# Enter code when prompted

# Connect (use the wireless debugging IP:port from main screen)
adb connect <ip:debugging_port>

# Verify
adb devices

# Install APK
adb install <path_to_apk>

# Uninstall
adb uninstall <package_name>

# Push file to Downloads
adb push <local_path> //sdcard//Download//<filename>
```

## Pitfalls

- **MSYS/Git Bash path conversion**: Use `//sdcard//` not `/sdcard/` — MSYS converts `/sdcard` to a Windows path
- **"Install via USB"** must be enabled on Xiaomi devices: Developer Options → "Install via USB" → enable. May require Mi account login. **Re-enables after each uninstall.**
- **Pairing vs Connection ports are DIFFERENT**: Pairing uses a separate port shown when you tap "Pair device with pairing code". Connection uses the main wireless debugging port.
- **Connection drops**: WiFi ADB disconnects when phone sleeps or switches networks. Use `adb disconnect` then `adb connect` to reconnect.
- **Timeout on install**: If `adb install` times out, try `adb disconnect` → `adb connect` → retry
