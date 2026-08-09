#!/usr/bin/env python3
"""Fail-closed guard for the canonical knowledge-delta history.

The current ledger may append new events, but every event that already existed in
an earlier Git ref must remain byte-equivalent after canonical JSON
serialization. Deletion, reordering, duplicate IDs or mutation of historical
events fails the check.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = Path("data/knowledge-deltas.json")


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def event_hash(event: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(event)).hexdigest()


def load_current() -> dict[str, Any]:
    return json.loads((ROOT / LEDGER_PATH).read_text(encoding="utf-8"))


def load_from_git(ref: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{LEDGER_PATH.as_posix()}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Baseline {ref!r} nicht lesbar: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def validate_structure(ledger: dict[str, Any], label: str) -> list[dict[str, Any]]:
    items = ledger.get("items")
    if not isinstance(items, list):
        raise ValueError(f"{label}: items fehlt oder ist keine Liste")
    ids = [item.get("event_id") for item in items if isinstance(item, dict)]
    if len(ids) != len(items) or any(not isinstance(event_id, str) for event_id in ids):
        raise ValueError(f"{label}: jeder Eintrag braucht event_id")
    if len(set(ids)) != len(ids):
        raise ValueError(f"{label}: doppelte event_id")
    if ids != sorted(ids):
        raise ValueError(f"{label}: Ereignisse sind nicht monoton nach event_id geordnet")
    return items


def verify_append_only(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    old_items = validate_structure(baseline, "Baseline")
    new_items = validate_structure(current, "Aktuell")

    old_ids = [item["event_id"] for item in old_items]
    new_ids = [item["event_id"] for item in new_items]
    if new_ids[: len(old_ids)] != old_ids:
        raise ValueError("Historische Ereignisse wurden gelöscht, umgeordnet oder in der Mitte eingefügt")

    for index, old_event in enumerate(old_items):
        new_event = new_items[index]
        if event_hash(old_event) != event_hash(new_event):
            raise ValueError(f"Historisches Ereignis verändert: {old_event['event_id']}")

    appended = new_items[len(old_items) :]
    return {
        "status": "PASS",
        "baseline_events": len(old_items),
        "current_events": len(new_items),
        "appended_events": [item["event_id"] for item in appended],
        "history_prefix_hash": hashlib.sha256(canonical(old_items)).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-ref", required=True, help="Git-Ref des unveränderten Ausgangsstands")
    args = parser.parse_args()
    try:
        result = verify_append_only(load_from_git(args.baseline_ref), load_current())
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
