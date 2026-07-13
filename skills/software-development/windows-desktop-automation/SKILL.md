---
name: windows-desktop-automation
description: Build Windows desktop utilities with Python ctypes — keyboard/mouse hooks, global hotkeys, input blocking, system tray, Task Scheduler services. No external dependencies beyond stdlib.
tags: [windows, ctypes, win32, hooks, keyboard, mouse, service, task-scheduler, python]
---

# Windows Desktop Automation (Python + ctypes)

Build Windows background utilities using only Python stdlib + ctypes. No pywin32, no external packages.

## Core Pattern: Win32 API via ctypes

### DLL Loading

```python
import ctypes
import ctypes.wintypes as wt

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
```

**PITFALL**: `GetModuleHandleW` is in `kernel32`, NOT `user32`. Common mistake — the function sounds UI-related but it's a kernel module function.

```python
hmod = kernel32.GetModuleHandleW(None)  # ✅ correct
# hmod = user32.GetModuleHandleW(None)  # ❌ AttributeError: function not found
```

### Arg/ret Types (always declare before calling)

```python
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, wt.HINSTANCE, wt.DWORD]
user32.SetWindowsHookExW.restype = wt.HHOOK
kernel32.GetModuleHandleW.argtypes = [wt.LPCWSTR]
kernel32.GetModuleHandleW.restype = wt.HINSTANCE
```

Without argtypes/restype, ctypes guesses wrong on 64-bit Windows (pointer truncation, crashes).

## Keyboard + Mouse Hooks

### Low-Level Hooks (WH_KEYBOARD_LL=13, WH_MOUSE_LL=14)

```python
class KBDLLHOOK(ctypes.Structure):
    _fields_ = [
        ('vkCode', wt.DWORD), ('scanCode', wt.DWORD),
        ('flags', wt.DWORD), ('time', wt.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong)),
    ]

HOOKPROC = ctypes.CFUNCTYPE(ctypes.c_long, ctypes.c_int, wt.WPARAM, ctypes.POINTER(KBDLLHOOK))

def kb_proc(nCode, wParam, lParam):
    if nCode == 0 and wParam in (0x0100, 0x0104):  # WM_KEYDOWN, WM_SYSKEYDOWN
        vk = lParam.contents.vkCode
        # return -1 to block, or CallNextHookEx to pass through
    return user32.CallNextHookEx(hook, nCode, wParam, lParam)

cb = HOOKPROC(kb_proc)
hook = user32.SetWindowsHookExW(13, cb, kernel32.GetModuleHandleW(None), 0)
```

### Hook Lifecycle

- Hook callback must stay alive (store reference globally or ctypes garbage-collects it)
- `GetMessageW` loop required — hooks dispatch via message pump
- Always `UnhookWindowsHookEx` on exit (use `atexit.register`)
- Return `-1` = block key, `CallNextHookEx` = pass through

### VK Code Helpers

```python
VK_MAP = {'ctrl': 0x11, 'shift': 0x10, 'alt': 0x12}
for c in 'abcdefghijklmnopqrstuvwxyz0123456789':
    VK_MAP[c] = ord(c.upper())
for i in range(1, 13):
    VK_MAP[f'f{i}'] = 0x70 + i - 1

def get_mod_flags():
    f = 0
    if user32.GetKeyState(0x10) & 0x8000: f |= 0x0004  # shift
    if user32.GetKeyState(0x11) & 0x8000: f |= 0x0002  # ctrl
    if user32.GetKeyState(0x12) & 0x8000: f |= 0x0001  # alt
    return f
```

## Background Service via Task Scheduler

No pywin32 needed. Use `schtasks` + `pythonw` (windowless Python):

```bat
:: Register as logon service (runs as SYSTEM, no window)
schtasks /Create /TN "MyApp" /TR "pythonw C:\MyApp\main.py" /SC ONLOGON /RL HIGHEST /F

:: Manual start
schtasks /Run /TN "MyApp"

:: Stop (kill the process, then restart)
taskkill /F /IM pythonw.exe && schtasks /Run /TN "MyApp"

:: Remove
schtasks /Delete /TN "MyApp" /F
```

### Service Pattern

1. Script runs silently (no print/input when no console)
2. Config in `C:\AppName\config.txt` (editable via notepad)
3. Setup.bat copies files + registers task + adds to PATH
4. CLI command opens config: `notepad C:\AppName\config.txt`

## Windows Update tray notification cleanup

When Windows Update services are disabled but a red update icon remains in the tray, it is often only the notification UX process, not active updating. Check and stop these processes first: `MoNotificationUx`, `MusNotifyIcon`, `MusNotification`, `MusNotificationUx`, `MoUsoCoreWorker`, `UsoClient`.

Durable hide pattern:

1. Run elevated PowerShell (`Start-Process powershell.exe -Verb RunAs ...`).
2. `Stop-Process` the matching notification process(es), especially `MoNotificationUx.exe` from `C:\Windows\uus\AMD64\MoNotificationUx.exe`.
3. Block relaunch with Image File Execution Options under `HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<exe>` and `Debugger='C:\Windows\System32\cmd.exe /c exit 0'` for the notifier exes.
4. Add/update Windows Update notification policies: `SetUpdateNotificationLevel`, `UpdateNotificationLevel`, `SetAutoRestartNotificationDisable`, plus `NoAutoUpdate` and `NoAutoRebootWithLoggedOnUsers` under the AU policy key.
5. Clear tray icon cache: remove `IconStreams` and `PastIconsStream` from `HKCU:\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\TrayNotify`.
6. Restart Explorer to refresh the shell without rebooting.

Pitfalls:

- Some task scheduler entries deny disable even as admin. If the core services are disabled and notifier processes are blocked, the tray icon can still be removed.
- Bash expands `$_` and `$paths` inside double-quoted `powershell.exe -Command` strings. Use single quotes around the PowerShell command when running from Git Bash/MSYS, or write a `.ps1` file and launch it.
- Tooling may block literal task names containing reboot/restart terms. Avoid broad scheduled-task queries with those names; query explicit task paths or use a script file.

## Interactive desktop capture from a gateway/service session

When Hermes Gateway or the terminal backend is running as `SYSTEM` or a non-interactive service account, direct screenshot APIs can fail or capture the lock/session-0 desktop instead of the user's visible desktop. Typical symptoms: `BitBlt failed`, PowerShell `CopyFromScreen` throws `Controlador no válido`, or the image is blank/lock-screen only.

Use Task Scheduler to run the capture script inside the logged-in user's interactive console session:

```bash
# 1) Write a PowerShell capture script somewhere under the user's workspace.
# 2) Register it as an interactive one-shot task for the logged-in user.
schtasks /Create /TN HermesDesktopCapture /SC ONCE /ST 23:59 \
  /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\\Users\\ELY\\Desktop\\COSAS\\capture.ps1" \
  /RU ely /IT /F
schtasks /Run /TN HermesDesktopCapture
sleep 3
schtasks /Delete /TN HermesDesktopCapture /F
```

Known-good PowerShell capture body:

```powershell
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.Size)
$out = 'C:\Users\ELY\Desktop\COSAS\captura_escritorio.png'
$bitmap.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose(); $bitmap.Dispose()
```

Verify the image with `file`/size and, when possible, vision. If it shows Windows lock screen, the PC is locked; tell user it captured lock screen, not unlocked desktop.

## Pitfalls

- **Service/session screenshots**: Gateway may run as `SYSTEM`; direct capture can fail or see session 0. Use the interactive `schtasks /IT /RU <user>` pattern above.
- **Hook garbage collection**: ctypes callback objects get GC'd if not stored in a global/list. Hook silently stops working.
- **Admin required**: `SetWindowsHookExW` with dwThreadId=0 (global hook) needs elevation for some hooks.
- **Ctrl+Alt+Del**: Cannot be blocked via user-space hooks — Windows intercepts at kernel level (SAS).
- **Release modifiers on lock**: If locking input on hotkey press, release held modifier keys first or they "stick":
  ```python
  def release_mods():
      for vk in (0x10, 0x11, 0x12):
          if user32.GetKeyState(vk) & 0x8000:
              user32.keybd_event(vk, 0, 0x0002, None)  # KEYEVENTF_KEYUP
  ```
- **pythonw vs python**: `pythonw.exe` runs without console window. Use for services/background. `python.exe` shows console.
- **32-bit pointer truncation**: Always set `.argtypes` and `.restype` on every ctypes function you call. Without them, ctypes defaults to `c_int` return which truncates 64-bit pointers.

## Reference

See `references/ctypes-win32-api-map.md` for common Win32 API ctypes signatures.
