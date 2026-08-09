from __future__ import annotations

from pathlib import Path
import argparse
import json
import re

from canonical_json import sha256_json
from preflight import preflight

ROOT = Path(__file__).resolve().parents[1]
PREFIX = {
    "beobachtung": "OBS",
    "erkenntnis": "ERK",
    "regel": "RULE",
    "standard": "STD",
    "goldene_regel": "GOLD",
    "fehler": "ERROR",
    "anti_pattern": "ANTI",
    "wenn_dann": "WHEN",
    "automatisierung": "AUTO",
    "notiz": "NOTE",
    "offene_frage": "OPEN",
    "entscheidung": "DEC",
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def next_entry_id(entry_type: str, seed: list[dict]) -> str:
    prefix = PREFIX[entry_type]
    numbers = []
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    for entry in seed:
        match = pattern.match(entry.get("id", ""))
        if match:
            numbers.append(int(match.group(1)))
    return f"{prefix}-{max(numbers, default=0) + 1:03d}"


def candidate_to_entry(candidate: dict, seed: list[dict]) -> dict:
    entry = {
        "id": next_entry_id(candidate["type"], seed),
        "type": candidate["type"],
        "title": candidate["title"],
        "summary": candidate["summary"],
        "primary_category": candidate["primary_category"],
        "categories": list(candidate.get("categories", [])),
        "tags": list(candidate.get("tags", [])),
        "projects": list(candidate.get("projects", ["PROVOWARE Knowledge & Project Intelligence"])),
        "priority": candidate["priority"],
        "maturity": candidate["maturity"],
        "scope": candidate["scope"],
        "automatable": bool(candidate.get("automatable", False)),
        "status": "bestaetigt" if candidate["maturity"] not in {"E0", "E1"} else "neu",
        "revision": 1,
        "sources": list(candidate["sources"]),
    }
    if candidate.get("relationships"):
        entry["relationships"] = list(candidate["relationships"])
    return entry


def build_preview(candidate: dict, seed: list[dict], plan_number: int = 1) -> dict:
    check = preflight(candidate, seed)
    plan_id = f"PLAN-{plan_number:04d}"
    undo_id = f"UNDO-{plan_number:04d}"

    if check["result"] != "READY":
        return {
            "plan_id": plan_id,
            "schema_version": "1.0",
            "candidate_id": candidate.get("candidate_id"),
            "operation": "blocked",
            "result": "PREVIEW_BLOCKED",
            "reason": f"Preflight-Zustand {check['result']} erlaubt keinen Create-Plan.",
            "before": None,
            "after": None,
            "before_hash": None,
            "after_hash": None,
            "delta_preview": None,
            "undo_preview": {
                "undo_id": undo_id,
                "schema_version": "1.0",
                "plan_id": plan_id,
                "operation": "none",
                "target_entry_id": None,
                "restore_snapshot": None,
                "restore_hash": None,
                "status": "NOT_APPLICABLE",
            },
        }

    after = candidate_to_entry(candidate, seed)
    after_hash = sha256_json(after)
    delta = {
        "schema_version": "1.0",
        "entry_id": after["id"],
        "change_type": "neu",
        "reason": f"Vorschau einer möglichen Übernahme von {candidate['candidate_id']}.",
        "before_hash": None,
        "after_hash": after_hash,
        "status": "PREVIEW_ONLY",
    }
    undo = {
        "undo_id": undo_id,
        "schema_version": "1.0",
        "plan_id": plan_id,
        "operation": "delete_created_entry",
        "target_entry_id": after["id"],
        "restore_snapshot": None,
        "restore_hash": None,
        "status": "PREVIEW_ONLY",
    }
    return {
        "plan_id": plan_id,
        "schema_version": "1.0",
        "candidate_id": candidate["candidate_id"],
        "operation": "create",
        "result": "PREVIEW_READY",
        "reason": "Deterministische Vorprüfung READY; keine kanonischen Daten werden verändert.",
        "before": None,
        "after": after,
        "before_hash": None,
        "after_hash": after_hash,
        "delta_preview": delta,
        "undo_preview": undo,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Erzeugt ausschließlich eine reversible Übernahmevorschau.")
    parser.add_argument("candidate_id")
    args = parser.parse_args()

    inbox = _load(ROOT / "data" / "inbox.json")["items"]
    seed = _load(ROOT / "data" / "masterbook_seed.json")
    candidate = next((item for item in inbox if item["candidate_id"] == args.candidate_id), None)
    if candidate is None:
        raise SystemExit(f"Unbekannter Kandidat: {args.candidate_id}")

    preview = build_preview(candidate, seed)
    print(json.dumps(preview, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if preview["result"] == "PREVIEW_READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
