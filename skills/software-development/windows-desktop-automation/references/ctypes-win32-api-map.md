# Win32 API ctypes Quick Reference

## kernel32.dll

| Function | argtypes | restype |
|---|---|---|
| `GetModuleHandleW` | `[wt.LPCWSTR]` | `wt.HINSTANCE` |
| `GetLastError` | `[]` | `wt.DWORD` |
| `Sleep` | `[wt.DWORD]` | `None` |

## user32.dll

| Function | argtypes | restype |
|---|---|---|
| `SetWindowsHookExW` | `[c_int, c_void_p, wt.HINSTANCE, wt.DWORD]` | `wt.HHOOK` |
| `CallNextHookEx` | `[wt.HHOOK, c_int, wt.WPARAM, c_void_p]` | `c_long` |
| `UnhookWindowsHookEx` | `[wt.HHOOK]` | `wt.BOOL` |
| `GetMessageW` | `[POINTER(wt.MSG), wt.HWND, c_uint, c_uint]` | `wt.BOOL` |
| `GetKeyState` | `[c_int]` | `c_short` |
| `GetAsyncKeyState` | `[c_int]` | `c_short` |
| `keybd_event` | `[wt.BYTE, wt.BYTE, wt.DWORD, POINTER(c_ulong)]` | `None` |
| `SetCursorPos` | `[c_int, c_int]` | `wt.BOOL` |
| `ShowCursor` | `[wt.BOOL]` | `c_int` |
| `RegisterHotKey` | `[wt.HWND, c_int, c_uint, c_uint]` | `wt.BOOL` |

## Hook Constants

| Constant | Value | Use |
|---|---|---|
| `WH_KEYBOARD_LL` | 13 | Low-level keyboard hook |
| `WH_MOUSE_LL` | 14 | Low-level mouse hook |
| `HC_ACTION` | 0 | nCode: process the message |
| `WM_KEYDOWN` | 0x0100 | Key press |
| `WM_KEYUP` | 0x0101 | Key release |
| `WM_SYSKEYDOWN` | 0x0104 | Alt+key press |
| `WM_MOUSEMOVE` | 0x0200 | Mouse move |
| `WM_LBUTTONDOWN` | 0x0201 | Left click |
| `WM_RBUTTONDOWN` | 0x0204 | Right click |

## Modifier Flag Values (for GetKeyState / RegisterHotKey)

| Modifier | GetKeyState VK | RegisterHotKey MOD |
|---|---|---|
| Shift | `0x10` | `0x0004` |
| Ctrl | `0x11` | `0x0002` |
| Alt | `0x12` | `0x0001` |

## Return Values from Hook Callback

- Return `-1` (or `LRESULT(-1)`) → block the input
- Return `CallNextHookEx(...)` → pass to next hook / target window

## KBDLLHOOKSTRUCT Fields

- `vkCode` — Virtual key code (0x41='A', 0x0D=Enter, etc.)
- `scanCode` — Hardware scan code
- `flags` — Bit 4 (`0x10`) = injected, Bit 5 (`0x20`) = alt-down
- `time` — Timestamp
- `dwExtraInfo` — Extra info (usually pointer to ULONG)

## MSLLHOOKSTRUCT Fields

- `pt` — POINT (x, y) cursor position
- `mouseData` — Wheel delta or X button (HIWORD)
- `flags` — `LLMHF_INJECTED=0x01`
- `time` — Timestamp
