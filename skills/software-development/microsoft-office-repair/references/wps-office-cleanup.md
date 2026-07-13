# WPS Office triage and cleanup on Windows

Use when a user says WPS Office is stuck in read-only mode, blocks saving/editing behind a paid upsell, or asks to remove WPS completely.

## Boundaries
- Do not help bypass WPS Pro/Premium licensing or activation.
- Explain that basic document editing may be free, but paid prompts can appear for premium formats/features.
- If Windows file properties show "This file came from another computer" / `Desbloquear`, have the user tick **Unblock/Desbloquear**, Apply, then reopen the document.
- If the user wants a free full editor, recommend LibreOffice or Google Docs.

## Cleanup workflow used successfully
Commands shown for Hermes Windows bash/MSYS session; adjust paths per user.

1. Close WPS processes:
```bash
taskkill.exe /IM wps.exe /F 2>/dev/null || true
taskkill.exe /IM wpscloudsvr.exe /F 2>/dev/null || true
taskkill.exe /IM wpp.exe /F 2>/dev/null || true
taskkill.exe /IM et.exe /F 2>/dev/null || true
```

2. Find official uninstaller under user-local Kingsoft install:
```bash
# Typical path:
'C:/Users/<USER>/AppData/Local/Kingsoft/WPS Office/<version>/utility/uninst.exe' /S
```

3. Remove safe leftovers after uninstall:
```bash
rm -rf "$LOCALAPPDATA/Kingsoft" "$APPDATA/kingsoft" "$PROGRAMDATA/Kingsoft"
rm -rf "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS Office"
rm -f "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS Office.lnk" \
      "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS Docs.lnk" \
      "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS Sheets.lnk" \
      "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS Slides.lnk" \
      "$APPDATA/Microsoft/Windows/Start Menu/Programs/WPS PDF.lnk" \
      "$APPDATA/Microsoft/Internet Explorer/Quick Launch/User Pinned/TaskBar/WPS Office.lnk"
```

4. Verify:
```bash
tasklist.exe 2>/dev/null | grep -iE 'wps|kingsoft|wpp|et.exe' || true
winget list --name WPS 2>/dev/null || true
for p in "$LOCALAPPDATA/Kingsoft" "$APPDATA/kingsoft" "$PROGRAMDATA/Kingsoft"; do
  [ -e "$p" ] && printf 'EXISTS %s\n' "$p" || printf 'gone %s\n' "$p"
done
cmd.exe /c assoc .docx 2>/dev/null || true
```

Expected: no WPS/Kingsoft processes, no WPS in winget, Kingsoft dirs gone. `.docx` may return `Word.Document.12` or another non-WPS association depending on installed apps.
