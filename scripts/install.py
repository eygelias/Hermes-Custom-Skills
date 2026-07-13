#!/usr/bin/env python3
"""Install this backup's skills into a Hermes profile."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def default_home() -> Path:
    if value := os.environ.get("HERMES_HOME"):
        return Path(value).expanduser()
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "hermes"
    return Path.home() / ".hermes"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hermes-home", type=Path, default=default_home())
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads((REPO / "inventory.json").read_text(encoding="utf-8"))
    target_root = args.hermes_home / "skills"
    installed = skipped = 0

    for item in data["skills"]:
        rel = Path(item["path"])
        source = REPO / "skills" / rel
        target = target_root / rel
        if not (source / "SKILL.md").is_file():
            raise FileNotFoundError(f"Backup incomplete: {source / 'SKILL.md'}")
        if target.exists() and not args.force:
            print(f"SKIP existing: {item['name']}")
            skipped += 1
            continue
        print(f"INSTALL: {item['name']} -> {target}")
        if not args.dry_run:
            if target.exists():
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target)
        installed += 1

    print(f"Installed/planned: {installed}; skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
