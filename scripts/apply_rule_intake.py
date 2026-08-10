#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data/masterbook_seed.json"
DELTAS = ROOT / "data/knowledge-deltas.json"
SEED_JS = ROOT / "src/seed.js"
DELTAS_JS = ROOT / "src/deltas.js"
DEFAULT_CANDIDATE = ROOT / "evidence/I015_2G_RULE_015_KANDIDAT.json"


def compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(candidate: dict[str, Any], seed: list[dict[str, Any]], ledger: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    rule = candidate.get("zielregel")
    delta = candidate.get("zieldelta")
    if not isinstance(rule, dict) or not isinstance(delta, dict):
        raise ValueError("zielregel/zieldelta fehlen")
    if rule.get("id") != "RULE-015" or delta.get("event_id") != "DELTA-0016":
        raise ValueError("unerwartete Ziel-IDs")
    if rule.get("maturity") not in {"E0", "E1", "E2"}:
        raise ValueError("Reifegrad darf E2 nicht ueberschreiten")
    if candidate.get("goldene_regel") is not False:
        raise ValueError("Goldene-Regel-Hochstufung ist unzulaessig")
    if delta.get("entry_id") != rule.get("id"):
        raise ValueError("Delta verweist nicht auf Zielregel")

    rule_ids = [item.get("id") for item in seed if isinstance(item, dict)]
    if rule["id"] in rule_ids:
        raise ValueError("RULE-015 existiert bereits")
    if not rule_ids or rule_ids[-1] != "RULE-014":
        raise ValueError("Seed endet nicht bei RULE-014")

    items = ledger.get("items")
    if not isinstance(items, list):
        raise ValueError("Delta-Ledger items fehlt")
    delta_ids = [item.get("event_id") for item in items if isinstance(item, dict)]
    if delta["event_id"] in delta_ids:
        raise ValueError("DELTA-0016 existiert bereits")
    if not delta_ids or delta_ids[-1] != "DELTA-0015":
        raise ValueError("Delta-Ledger endet nicht bei DELTA-0015")

    rule = json.loads(json.dumps(rule, ensure_ascii=False))
    delta = json.loads(json.dumps(delta, ensure_ascii=False))
    delta["before_hash"] = None
    delta["after_hash"] = sha256(rule)
    return rule, delta


def planned_state(candidate_path: Path) -> dict[str, Any]:
    candidate = load(candidate_path)
    seed = load(SEED)
    ledger = load(DELTAS)
    if not isinstance(seed, list) or not isinstance(ledger, dict):
        raise ValueError("kanonische Datenstruktur ungueltig")
    rule, delta = validate(candidate, seed, ledger)

    next_seed = [*seed, rule]
    next_ledger = json.loads(json.dumps(ledger, ensure_ascii=False))
    next_ledger["items"] = [*ledger["items"], delta]
    seed_js = f"window.MASTERBOOK_SEED={compact(next_seed)};\n"
    deltas_js = f"window.KNOWLEDGE_DELTAS = {compact(next_ledger)};\n"
    return {
        "seed": next_seed,
        "ledger": next_ledger,
        "seed_js": seed_js,
        "deltas_js": deltas_js,
        "receipt": {
            "schema_version": "1.0",
            "status": "READY",
            "rule_id": rule["id"],
            "delta_id": delta["event_id"],
            "rule_hash": sha256(rule),
            "seed_hash": sha256(next_seed),
            "delta_ledger_hash": sha256(next_ledger),
            "writes": [
                "data/masterbook_seed.json",
                "data/knowledge-deltas.json",
                "src/seed.js",
                "src/deltas.js"
            ]
        },
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def apply(state: dict[str, Any]) -> None:
    atomic_write(SEED, compact(state["seed"]) + "\n")
    atomic_write(DELTAS, compact(state["ledger"]) + "\n")
    atomic_write(SEED_JS, state["seed_js"])
    atomic_write(DELTAS_JS, state["deltas_js"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed RULE-Aufnahme aus qualifizierter Evidence")
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--apply", action="store_true", help="Vier kanonische/abgeleitete Dateien schreiben")
    args = parser.parse_args()
    try:
        state = planned_state(args.candidate)
        if args.apply:
            apply(state)
            state["receipt"]["status"] = "APPLIED"
        print(json.dumps(state["receipt"], ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
