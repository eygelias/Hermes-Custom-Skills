#!/usr/bin/env python3
"""Discover NVIDIA Build Free Endpoint chat models usable by Hermes.

Requires NVIDIA_API_KEY in environment. Prints a Python tuple of API model IDs
that are both:
  1. listed on build.nvidia.com with nim_type_preview / Free Endpoint, and
  2. present in https://integrate.api.nvidia.com/v1/models for the key, and
  3. marked playgroundType=chat in the Build page data.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from difflib import get_close_matches

BUILD_URL = "https://build.nvidia.com/models?filters=nimType%3Anim_type_preview&page={}"
API_MODELS_URL = "https://integrate.api.nvidia.com/v1/models"
UA = "Mozilla/5.0 hermes-skill/nvidia-free-preview"


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "ignore")


def fetch_api_model_ids(api_key: str) -> set[str]:
    req = urllib.request.Request(
        API_MODELS_URL,
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json", "User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    items = data.get("data", []) if isinstance(data, dict) else data
    return {m["id"] for m in items if isinstance(m, dict) and isinstance(m.get("id"), str)}


def extract_resources(html: str) -> list[dict]:
    # Next/RSC payload contains escaped JSON fragments like \"resources\":[{...}].
    text = html.replace('\\"', '"')
    out: list[dict] = []
    pos = 0
    while True:
        idx = text.find('"resources":[{', pos)
        if idx < 0:
            break
        start = text.find("[", idx)
        try:
            arr, _ = json.JSONDecoder().raw_decode(text[start:])
        except Exception:
            pos = idx + 20
            continue
        if arr and isinstance(arr[0], dict) and "resourceId" in arr[0]:
            out.extend(arr)
            break
        pos = idx + 20
    return out


def label_values(resource: dict, key: str) -> list[str]:
    for label in resource.get("labels", []):
        if label.get("key") == key:
            return label.get("values", []) or []
    return []


def normalize_candidates(model_id: str) -> list[str]:
    pub, name = model_id.split("/", 1)
    candidates = [model_id, f"{pub}/{name.replace('_', '.')}", f"{pub}/{name.replace('_', '-')}"]
    aliases = {
        "mistralai/mixtral-8x7b-instruct": "mistralai/mixtral-8x7b-instruct-v0.1",
        "upstage/solar-10_7b-instruct": "upstage/solar-10.7b-instruct",
    }
    if model_id in aliases:
        candidates.append(aliases[model_id])
    return candidates


def main() -> int:
    api_key = os.getenv("NVIDIA_API_KEY", "").strip()
    if not api_key:
        print("Set NVIDIA_API_KEY first", file=sys.stderr)
        return 2

    api_ids = fetch_api_model_ids(api_key)
    resources: list[dict] = []
    for page in range(1, 5):
        resources.extend(extract_resources(fetch_text(BUILD_URL.format(page))))

    seen: dict[str, dict] = {}
    for r in resources:
        publisher = (label_values(r, "publisher") or [r.get("orgName", "")])[0]
        name = r.get("name")
        if publisher and name:
            seen[f"{publisher}/{name}"] = r

    selected: list[str] = []
    unresolved: list[str] = []
    for model_id, resource in seen.items():
        if "chat" not in [v.lower() for v in label_values(resource, "playgroundType")]:
            continue
        found = next((c for c in normalize_candidates(model_id) if c in api_ids), None)
        if found:
            if found not in selected:
                selected.append(found)
        else:
            unresolved.append(model_id)

    print(f"# free_endpoint_resources={len(seen)} chat_api_models={len(selected)} unresolved_chat={len(unresolved)}")
    print("FREE_PREVIEW_CHAT_MODELS = (")
    for mid in selected:
        print(f'    "{mid}",')
    print(")")
    if unresolved:
        print("# unresolved:", ", ".join(unresolved), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
