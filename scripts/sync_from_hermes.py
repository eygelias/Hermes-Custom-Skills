#!/usr/bin/env python3
"""Copy the inventoried non-bundled skills from a Hermes profile into this repo."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INVENTORY = REPO / "inventory.json"
IGNORED = {".git", "__pycache__", ".DS_Store", "Thumbs.db", ".env", "auth.json", "config.yaml"}


def default_home() -> Path:
    if value := os.environ.get("HERMES_HOME"):
        return Path(value).expanduser()
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "hermes"
    return Path.home() / ".hermes"


def ignore(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED or name.endswith((".pyc", ".pyo"))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hermes-home", type=Path, default=default_home())
    args = parser.parse_args()

    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    source_root = args.hermes_home / "skills"
    target_root = REPO / "skills"
    copied = 0
    missing: list[str] = []

    for item in data["skills"]:
        rel = Path(item["path"])
        source = source_root / rel
        target = target_root / rel
        if not (source / "SKILL.md").is_file():
            missing.append(f"{item['name']}: {source}")
            continue
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, ignore=ignore)
        copied += 1

    print(f"Copied {copied}/{data['expected_count']} local skills from {source_root}")
    if missing:
        print("Missing:")
        print("\n".join(f"- {entry}" for entry in missing))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
