---
name: office-suite-management
description: Manage free/desktop office suites on Windows — WPS Office and LibreOffice install/uninstall, document language/orthography fixes, file associations, and safe cleanup.
tags: [windows, office, libreoffice, wps, documents, docx, uninstall, spellcheck]
triggers:
  - WPS Office blocks editing, read-only mode, premium/paywall prompts
  - User wants WPS Office or LibreOffice fully removed
  - LibreOffice shows every word misspelled or wrong language
  - Need to set Spanish/Venezuela orthography for DOCX documents
  - Need to clean office-suite leftovers and verify removal
---

# Office Suite Management

Use for non-Microsoft office suite issues on Windows: WPS Office, LibreOffice, DOCX language metadata, spellcheck dictionaries, and safe cleanup.

## User guidance style

For this user, act directly when possible. If GUI guidance needed, give short numbered steps and ask for a screenshot only after one clear action. Avoid multiple-choice flows.

## Diagnose WPS Office “read-only / update to unlock”

1. First check if Windows marked the file as downloaded-from-internet:
   - File → right-click → Properties → General → **Desbloquear**.
   - This is not the same as the **Solo lectura** checkbox.
2. If WPS blocks basic `Guardar como` behind Pro+, do not try to bypass licensing. Explain that crack/activation bypass is not supported.
3. Suggest true free alternatives:
   - Google Docs online
   - LibreOffice offline

## Fully remove WPS Office on Windows

WPS commonly installs per-user under `AppData\Local\Kingsoft` and may not appear in normal uninstall registries.

```bash
taskkill.exe /IM wps.exe /F 2>/dev/null || true
taskkill.exe /IM wpscloudsvr.exe /F 2>/dev/null || true
taskkill.exe /IM wpp.exe /F 2>/dev/null || true
taskkill.exe /IM et.exe /F 2>/dev/null || true
```

Find official uninstaller:

```bash
# Use search_files first if available; common path:
'C:/Users/ELY/AppData/Local/Kingsoft/WPS Office/<version>/utility/uninst.exe' /S
```

Then remove leftovers:

```bash
rm -rf "$LOCALAPPDATA/Kingsoft" "$APPDATA/kingsoft" "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS Office"
rm -f "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS Office.lnk" \
      "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS Docs.lnk" \
      "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS Sheets.lnk" \
      "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS Slides.lnk" \
      "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS PDF.lnk" \
      "$APPDATA/Microsoft/Internet Explorer/Quick Launch/User Pinned/TaskBar/WPS Office.lnk"
```

Verify:

```bash
tasklist.exe 2>/dev/null | grep -iE 'wps|kingsoft|wpp|et.exe' || true
winget list --name WPS 2>/dev/null || true
cmd.exe /c assoc .docx 2>/dev/null || true
```

## LibreOffice: fix all-red spellcheck for Spanish Venezuela

Root cause often: DOCX style language metadata is English (`<w:lang w:val="en"/>`) even though text is Spanish. Changing LibreOffice default language alone may not fix existing documents.

Check dictionaries exist:

```text
C:\Program Files\LibreOffice\share\extensions\dict-es\es_VE.dic
C:\Program Files\LibreOffice\share\extensions\dict-es\es_VE.aff
```

Set LibreOffice profile default locale in:

```text
C:\Users\<user>\AppData\Roaming\LibreOffice\4\user\registrymodifications.xcu
```

Patch `DefaultLocale`:

```xml
<value>es-VE</value>
```

For existing DOCX files, update `word/styles.xml` language tags to `es-VE`. Always create `.bak-es-ve` backup first.

See `references/libreoffice-spanish-venezuela-docx.md` for a tested script.

## Fully remove LibreOffice on Windows

1. Read uninstall key:

```bash
reg.exe query 'HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall' /s /f LibreOffice 2>/dev/null
```

2. Get product GUID and uninstall using MSI. Example:

```bash
msiexec.exe /x '{PRODUCT-GUID}' /qn /norestart
```

If elevation needed, run via elevated PowerShell:

```bash
powershell.exe -NoProfile -Command "Start-Process msiexec.exe -ArgumentList '/x {PRODUCT-GUID} /passive /norestart' -Verb RunAs -Wait"
```

3. Remove leftovers:

```bash
rm -rf '/c/Users/ELY/AppData/Roaming/LibreOffice' \
       '/c/Users/ELY/AppData/Local/LibreOffice' \
       '/c/ProgramData/LibreOffice'
rm -rf '/c/Program Files/LibreOffice'
```

If `Program Files` refuses with permission denied, remove with elevated PowerShell:

```bash
powershell.exe -NoProfile -Command "Start-Process powershell.exe -ArgumentList '-NoProfile -Command Remove-Item -LiteralPath ''C:\Program Files\LibreOffice'' -Recurse -Force -ErrorAction SilentlyContinue' -Verb RunAs -Wait"
```

4. Verify:

```bash
tasklist.exe 2>/dev/null | grep -iE 'soffice|libreoffice|swriter|scalc|simpress' || true
winget list --name LibreOffice 2>/dev/null || true
cmd.exe /c assoc .docx 2>/dev/null || true
```

## Pitfalls

- Do not promise WPS Pro features without payment. Free alternatives are allowed; bypassing license is not.
- Windows “Desbloquear” security marker can cause office apps to behave read-only even when the **Solo lectura** checkbox is off.
- LibreOffice may have correct Spanish dictionaries installed while an individual DOCX still uses English in `word/styles.xml`.
- On this Windows host, terminal uses Git Bash/MSYS. Use POSIX shell syntax, but Windows tools like `reg.exe`, `msiexec.exe`, `taskkill.exe`, and `cmd.exe /c assoc` work.
- Preserve user documents. Only remove application/config directories, never `Documents` files, unless explicitly requested.
