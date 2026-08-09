from __future__ import annotations

from pathlib import Path
import argparse
import json

from recovery_replay import classify_journal

ROOT = Path(__file__).resolve().parents[1]
BLOCKING = {"CORRUPT_JOURNAL", "HASH_MISMATCH", "RECOVERY_REQUIRED"}


def evaluate_write_gate(root: Path) -> dict:
    recovery = root / "recovery"
    journals = sorted(recovery.glob("TX-*.json")) if recovery.exists() else []
    classifications = []
    blocking_counts: dict[str, int] = {}

    for journal in journals:
        item = classify_journal(root, journal)
        compact = {
            "journal": item.get("journal", str(journal.relative_to(root))),
            "classification": item["classification"],
            "transaction_id": item.get("transaction_id"),
            "reason": item.get("reason"),
        }
        classifications.append(compact)
        if compact["classification"] in BLOCKING:
            blocking_counts[compact["classification"]] = blocking_counts.get(compact["classification"], 0) + 1

    if blocking_counts:
        status = "WRITE_BLOCKED"
        reason = "Mindestens ein Recovery-Journal besitzt keinen eindeutig sicheren Endzustand. Vor neuen Schreibvorgängen ist Recovery erforderlich."
    else:
        status = "WRITE_ALLOWED"
        reason = "Alle vorhandenen Recovery-Journale sind hashverifiziert abgeschlossen oder es existiert kein Journal."

    return {
        "schema_version": "1.0",
        "status": status,
        "checked_journals": len(journals),
        "blocking_counts": blocking_counts,
        "classifications": classifications,
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Schreibfreies Recovery-Startup-Gate vor PROVOWARE-Wissensmutationen.")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()
    result = evaluate_write_gate(Path(args.root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "WRITE_ALLOWED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
