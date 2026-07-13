# RAR Extraction on Windows

## Problem
RAR5 archives cannot be extracted with:
- `py7zr` — only handles 7z format, NOT RAR
- `rarfile` Python package — needs unrar CLI tool installed
- `7zr.exe` (standalone) — does NOT support RAR5
- `7za.exe` (7-Zip extra) — does NOT support RAR5

## Solution
Use WinRAR's UnRAR.exe — almost always installed on Windows gaming machines:

```
"C:\Program Files\WinRAR\UnRAR.exe" x -o+ -y "archive.rar" "output_dir\"
```

Flags:
- `x` = extract with full paths
- `-o+` = overwrite existing files
- `-y` = assume Yes on all queries

## Python integration
```python
import subprocess
result = subprocess.run(
    [r'C:\Program Files\WinRAR\UnRAR.exe', 'x', '-o+', '-y', rar_path, output_dir + '\\'],
    capture_output=True, text=True, timeout=120
)
```

## Notes
- The `unrar.exe` downloaded from rarlab.com is a GUI installer, NOT a console tool — it hangs
- WinRAR is typically at `C:\Program Files\WinRAR\UnRAR.exe` on Windows
- `file` command confirms RAR5: `RAR archive data, v5`
