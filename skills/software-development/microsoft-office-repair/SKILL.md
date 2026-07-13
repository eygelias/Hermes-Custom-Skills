---
name: microsoft-office-repair
description: Diagnose and fix Microsoft Office (365, LTSC, 2019, 2021) errors on Windows — broken Click-to-Run service, licensing failures, startup crashes, error codes 0x426-0x0 and similar.
tags: [windows, office, microsoft, troubleshooting, click-to-run, repair]
triggers:
  - Office error code (0x426-0x0, 0x30015, 0xc0000142, etc.)
  - "Word/Excel/Outlook won't open"
  - "Office se cierra solo"
  - Click-to-Run service missing or stopped
  - Office repair, reinstall, or licensing issues
---

# Microsoft Office Repair & Diagnostics

## When to use
When Microsoft Office (365, LTSC, 2019, 2021) fails to launch, crashes on startup, or shows error codes on Windows.

Also use as a lightweight triage entry point when a user says "Office" but is actually using another office suite (WPS Office, LibreOffice, Google Docs): identify the app first, avoid license-bypass help, and route to uninstall/cleanup or free alternatives when appropriate.

## Diagnostic sequence (ordered by cost)

### 1. Identify installation type
```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*","HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" 2>$null | Where-Object { $_.DisplayName -like "*Office*" -or $_.DisplayName -like "*Microsoft 365*" } | Select-Object DisplayName, DisplayVersion | Format-List
```
- **Click-to-Run (C2R)**: Most modern installs. Look for "Click-to-Run" components.
- **MSI**: Older installs. Repair via `msiexec /f{p|o|e|d|c|a|u|m|s|v} <product-code>`.
- **Microsoft Store**: Rare. Repair via Settings > Apps.

### 2. Check the Click-to-Run service
```cmd
sc query ClickToRunSvc
```
- **If missing (ERROR 1060)**: Installation is corrupt. Jump to Step 5 (repair/reinstall).
- **If stopped**: Try `sc start ClickToRunSvc` (needs admin). Set startup to automatic.
- **If running**: Service is OK, problem is elsewhere.

### 3. Try Word in safe mode
```cmd
start "" "C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE" /safe
```
- **If safe mode works and stays open**: Problem is an add-in. Disable add-ins via File > Options > Add-ins.
- **If safe mode also crashes**: Deeper issue (licensing, corrupt install). Continue diagnosis.

### 4. Check licensing
```powershell
Get-CimInstance -ClassName SoftwareLicensingProduct | Where-Object { $_.Name -like "*Office*" } | Select-Object Name, LicenseStatus, PartialProductKey | Format-List
```
- `LicenseStatus = 1` = licensed/activated
- `LicenseStatus = 0` = not activated
- For KMS: check if KMS host is reachable. Default GVLK key ending in `GCVGB` = Office LTSC 2024.
- **ospp.vbs no longer exists** in modern C2R installs — use PowerShell `SoftwareLicensingProduct` instead.

### 5. Online repair (from Control Panel)
```cmd
control.exe appwiz.cpl
```
Select Office → Change → **Online Repair** (NOT quick repair). The quick repair from Windows Settings does NOT fix C2R issues.

Or programmatically:
```cmd
"C:\Program Files\Common Files\Microsoft Shared\ClickToRun\OfficeC2RClient.exe" /repair user
```
This opens a GUI. For silent repair add `/quiet` but it still takes 10-20 minutes.

### 6. Uninstall + reinstall (nuclear option)
1. Download Microsoft Support and Recovery Assistant (SaRA): https://aka.ms/SaRA-OfficeRemoval
2. Run it to completely remove Office
3. Reinstall from https://account.microsoft.com > Services & subscriptions
4. **User files (Word/Excel documents) are NOT deleted** — only the application is removed

## Pitfalls

### ⛔ Do NOT try to manually register ClickToRunSvc
`sc create ClickToRunSvc binPath= "...OfficeC2RClient.exe /service"` creates a service entry but OfficeC2RClient.exe is NOT a proper Windows service binary. It times out on start with "service did not respond to start request." Always use the official repair/reinstall path instead.

### ⛔ Office Deployment Tool (ODT) extraction is NOT silent
The ODT setup.exe from `officecdn.microsoft.com` shows a EULA dialog even with `/quiet /extract:`. It cannot be scripted without user interaction. Don't waste time trying flags — either use the GUI or go straight to SaRA.

### ⛔ ospp.vbs does not exist in modern C2R installs
Don't look for `ospp.vbs` in the Office directory. It's not there. Use `Get-CimInstance -ClassName SoftwareLicensingProduct` via PowerShell for licensing info.

### ⛔ Quick repair from Windows Settings ≠ Online repair from Control Panel
Settings > Apps > Modify runs on the UWP package and does NOT fix Click-to-Run corruption. Always use Control Panel > Programs and Features for the real repair.

### ⛔ Service Control Manager errors from terminal need admin
`sc create`, `sc start`, `sc delete` all need elevation. Use `powershell -Command 'Start-Process sc -ArgumentList "..." -Verb RunAs -Wait'` and accept the UAC prompt.

## Key paths
- Office install: `C:\Program Files\Microsoft Office\root\Office16\`
- C2R client: `C:\Program Files\Common Files\Microsoft Shared\ClickToRun\OfficeC2RClient.exe`
- C2R registry: `HKLM\SOFTWARE\Microsoft\Office\ClickToRun\Configuration`
- License files: `C:\Program Files\Microsoft Office\root\Licenses16\`
- ODT download: `https://officecdn.microsoft.com/pr/wsus/setup.exe`

## Related office-suite cleanup notes
- `references/wps-office-cleanup.md` — WPS Office read-only/paywall triage, legal boundaries, silent uninstall path, leftover cleanup, and verification commands for Windows.

## User guidance notes
When guiding non-technical users through Office repair:
- Give numbered sequential steps, no multiple-choice questions
- Let the user drive (take screenshots, report back)
- Explain what each step does and what will happen
- Assure them their documents won't be deleted before uninstall/reinstall steps
