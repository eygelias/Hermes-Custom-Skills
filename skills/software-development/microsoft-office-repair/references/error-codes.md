# Office Error Codes Reference

## 0x426-0x0
**Meaning**: Corrupt or missing Click-to-Run installation/service. The Office C2R subsystem cannot initialize.
**Symptoms**: All Office apps fail to open. Error dialog says "Se ha producido un error" with suggestion to repair from Control Panel.
**Root causes**:
- ClickToRunSvc service deleted or never registered
- C2R client binaries corrupted
- Failed update left installation in broken state

**Fix sequence**:
1. `sc query ClickToRunSvc` — if ERROR 1060 (not found), installation is broken
2. Try OfficeC2RClient.exe /repair user — often insufficient
3. Full uninstall via SaRA + reinstall from Microsoft account
4. User documents are preserved through uninstall/reinstall

## 0x30015-11
**Meaning**: Update channel mismatch or blocked update.
**Fix**: Check `UpdateChannel` in `HKLM\SOFTWARE\Microsoft\Office\ClickToRun\Configuration`. Reset via ODT if needed.

## 0xC0000142
**Meaning**: Application failed to initialize properly (DLL load failure).
**Fix**: Often caused by corrupted Visual C++ redistributables. Repair VC++ runtimes first, then Office.

## Generic diagnostic commands
```powershell
# Office version and components
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | Where-Object { $_.DisplayName -like "*Office*" } | Select DisplayName, DisplayVersion

# License status
Get-CimInstance -ClassName SoftwareLicensingProduct | Where-Object { $_.Name -like "*Office*" } | Select Name, LicenseStatus, PartialProductKey

# C2R configuration
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Office\ClickToRun\Configuration"

# Recent Office errors in Event Log
Get-WinEvent -FilterHashtable @{LogName="Application"; Level=2} -MaxEvents 10 | Where-Object { $_.ProviderName -like "*Office*" } | Select TimeCreated, Message | Format-List
```
