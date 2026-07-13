#!/usr/bin/env python3
"""Verify RXPGuides UI locale coverage without touching guide content.

Run from addon root:
    python scripts/verify_rxpguides_ui_locale.py esES esMX

Checks:
- locale/localization_strings.lua + root/UI Lua L("...") and L"..." calls are present in each locale file
- format placeholders (%s, %d, %.0f%%, etc.) are preserved
- WoW color markers |c / |r counts are preserved
- locale/locales.xml parses
- Locale.lua recognizes each requested locale
- generated locale files have balanced double quotes per line
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path.cwd()
LOCALES = sys.argv[1:] or ["esES", "esMX"]


def extract_ui_strings(root: Path) -> set[str]:
    strings: set[str] = set()
    loc = (root / "locale" / "localization_strings.lua").read_text(encoding="utf-8-sig", errors="ignore")
    for m in re.finditer(r'L\["([^"]+)"\]\s*=', loc):
        strings.add(m.group(1))

    files = list(root.glob("*.lua")) + list((root / "UI").glob("**/*.lua"))
    call_patterns = [
        re.compile(r'(?<![A-Za-z0-9_.])L\s*\(\s*"([^"]+)"\s*\)'),
        re.compile(r'(?<![A-Za-z0-9_.])L\s*"([^"]+)"'),
        re.compile(r"(?<![A-Za-z0-9_.])L\s*\(\s*'([^']+)'\s*\)"),
        re.compile(r"(?<![A-Za-z0-9_.])L\s*'([^']+)'"),
    ]
    for path in files:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        for pat in call_patterns:
            strings.update(m.group(1) for m in pat.finditer(text))
    return strings


def parse_locale(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig", errors="ignore")
    return dict(re.findall(r'L\["([^"]+)"\]\s*=\s*"([^"]*)"', text))


def specs(text: str) -> list[str]:
    return re.findall(r'%(?:\d+\$)?[-+ #0]*(?:\d+)?(?:\.\d+)?[A-Za-z%]', text)


def quote_balance_bad_lines(path: Path) -> list[int]:
    bad: list[int] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        count = 0
        escaped = False
        for ch in line:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                count += 1
        if count % 2:
            bad.append(i)
    return bad


def main() -> int:
    strings = extract_ui_strings(ROOT)
    locale_lua = (ROOT / "Locale.lua").read_text(encoding="utf-8", errors="ignore")
    ET.parse(ROOT / "locale" / "locales.xml")
    locales_xml = (ROOT / "locale" / "locales.xml").read_text(encoding="utf-8", errors="ignore")

    ok = True
    for locale in LOCALES:
        path = ROOT / "locale" / f"{locale}.lua"
        data = parse_locale(path)
        missing = sorted(k for k in strings if k not in data)
        bad_specs = sorted(k for k in strings if k in data and specs(k) != specs(data[k]))
        bad_color = sorted(k for k in strings if k in data and (k.count("|r") != data[k].count("|r") or k.count("|c") != data[k].count("|c")))
        bad_quotes = quote_balance_bad_lines(path)
        registered = f'<Script file="{locale}.lua"/>' in locales_xml and f"locale == '{locale}'" in locale_lua
        print(f"{locale}: entries={len(data)} extracted={len(strings)} missing={len(missing)} bad_specs={len(bad_specs)} bad_color={len(bad_color)} quote_bad={len(bad_quotes)} registered={registered}")
        if missing:
            print("  missing sample:", missing[:20])
        if bad_specs:
            print("  placeholder sample:", bad_specs[:20])
        if bad_color:
            print("  color sample:", bad_color[:20])
        if bad_quotes:
            print("  quote lines:", bad_quotes[:20])
        ok = ok and not missing and not bad_specs and not bad_color and not bad_quotes and registered
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
