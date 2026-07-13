#!/usr/bin/env python3
"""Fail before publication when copied skills contain likely live secrets."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
TEXT_SUFFIXES = {".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".sh", ".ps1", ".html", ".css", ".svg", ".xml", ".csv"}
FORBIDDEN_NAMES = {".env", "auth.json", "config.yaml", "credentials.json", "service-account.json"}
SECRET_RULES = {
    "private-key": re.compile(r"(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github-token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "openai-style-key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "google-api-key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
}
WARNING_RULES = {
    "user-home-path": re.compile(r"(?i)(?:C:\\Users\\[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+)"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "private-ip": re.compile(r"\b(?:10\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)\d{1,3}\.\d{1,3}\b"),
}


def main() -> int:
    secrets: list[tuple[str, int, str]] = []
    warnings: list[tuple[str, int, str]] = []

    for path in SKILLS.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if path.name.lower() in FORBIDDEN_NAMES:
            secrets.append((rel, 0, "forbidden-file"))
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "SKILL.md":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for rule, pattern in SECRET_RULES.items():
                if pattern.search(line):
                    secrets.append((rel, number, rule))
            for rule, pattern in WARNING_RULES.items():
                if pattern.search(line):
                    warnings.append((rel, number, rule))

    print(f"Secret findings: {len(secrets)}")
    for rel, line, rule in secrets:
        print(f"ERROR {rel}:{line} [{rule}]")
    print(f"Privacy/portability warnings: {len(warnings)}")
    for rel, line, rule in warnings:
        print(f"WARN {rel}:{line} [{rule}]")
    return 1 if secrets else 0


if __name__ == "__main__":
    raise SystemExit(main())
