#!/usr/bin/env python3
"""Validate backup completeness and SKILL.md identity."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def skill_name(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    match = re.search(r"(?m)^name:\s*[\"']?([^\n\"']+)", text)
    return match.group(1).strip() if match else None


def main() -> int:
    data = json.loads((ROOT / "inventory.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    expected = {item["name"] for item in data["skills"]}
    found: set[str] = set()

    if len(expected) != data["expected_count"]:
        errors.append("inventory count or duplicate-name mismatch")

    for item in data["skills"]:
        path = ROOT / "skills" / item["path"] / "SKILL.md"
        if not path.is_file():
            errors.append(f"missing {path}")
            continue
        actual = skill_name(path)
        if actual != item["name"]:
            errors.append(f"name mismatch {path}: {actual!r} != {item['name']!r}")
        if actual:
            found.add(actual)

    for path in (ROOT / "skills").rglob("SKILL.md"):
        actual = skill_name(path)
        if actual and actual not in expected:
            errors.append(f"unexpected skill {actual}: {path}")

    print(f"Validated {len(found)}/{data['expected_count']} skills")
    for error in errors:
        print(f"ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
