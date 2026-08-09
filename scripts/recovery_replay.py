from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import os
import shutil

from canonical_json import canonical_json, sha256_json

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_JOURNAL_KEYS = {
    "schema_version", "transaction_id", "candidate_id", "intent_id", "state",
    "created_at", "updated_at", "targets", "applied_files", "error",
}
VALID_STATES = {
    "PREPARED", "WRITING", "VALIDATING", "COMMITTED", "ROLLED_BACK",
    "RECOVERY_REQUIRED", "FAILED",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_fsync(path: Path, payload, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "xb" if exclusive else "wb"
    data = (canonical_json(payload) + "\n").encode("utf-8")
    with path.open(mode) as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_dir(path.parent)


def _fsync_dir(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _state_hash(targets: list[dict], field: str) -> str:
    return sha256_json({target["path"]: target[field] for target in sorted(targets, key=lambda item: item["path"])})


def _validate_journal_shape(journal: dict) -> str | None:
    if not isinstance(journal, dict):
        return "Journal ist kein Objekt."
    missing = REQUIRED_JOURNAL_KEYS - set(journal)
    if missing:
        return f"Pflichtfelder fehlen: {sorted(missing)}"
    if journal.get("state") not in VALID_STATES:
        return f"Unbekannter Journalzustand: {journal.get('state')}"
    if not isinstance(journal.get("targets"), list) or len(journal["targets"]) < 3:
        return "Targets fehlen oder sind unvollständig."
    for target in journal["targets"]:
        for key in ("path", "before_hash", "after_hash", "backup_path", "temp_path"):
            if key not in target:
                return f"Target-Pflichtfeld fehlt: {key}"
    return None


def classify_journal(root: Path, journal_path: Path) -> dict:
    try:
        journal = _load(journal_path)
    except Exception as exc:
        return {
            "classification": "CORRUPT_JOURNAL",
            "journal": str(journal_path.relative_to(root)),
            "reason": f"{type(exc).__name__}: {exc}",
        }

    shape_error = _validate_journal_shape(journal)
    if shape_error:
        return {
            "classification": "CORRUPT_JOURNAL",
            "journal": str(journal_path.relative_to(root)),
            "transaction_id": journal.get("transaction_id"),
            "reason": shape_error,
        }

    observed_targets = []
    missing_paths = []
    for target in journal["targets"]:
        path = root / target["path"]
        if not path.exists():
            missing_paths.append(target["path"])
            continue
        try:
            observed_hash = sha256_json(_load(path))
        except Exception as exc:
            return {
                "classification": "HASH_MISMATCH",
                "journal": str(journal_path.relative_to(root)),
                "transaction_id": journal["transaction_id"],
                "reason": f"Zieldatei nicht lesbar: {target['path']}: {type(exc).__name__}: {exc}",
            }
        observed_targets.append({**target, "observed_hash": observed_hash})

    if missing_paths:
        return {
            "classification": "RECOVERY_REQUIRED",
            "journal": str(journal_path.relative_to(root)),
            "transaction_id": journal["transaction_id"],
            "reason": f"Zieldateien fehlen: {missing_paths}",
        }

    all_before = all(item["observed_hash"] == item["before_hash"] for item in observed_targets)
    all_after = all(item["observed_hash"] == item["after_hash"] for item in observed_targets)
    state = journal["state"]

    if state == "COMMITTED":
        classification = "COMMITTED_VERIFIED" if all_after else "HASH_MISMATCH"
    elif state == "ROLLED_BACK":
        classification = "ROLLED_BACK_VERIFIED" if all_before else "HASH_MISMATCH"
    elif state in {"PREPARED", "WRITING", "VALIDATING", "FAILED"}:
        if all_after:
            classification = "COMMITTED_VERIFIED"
        elif all_before:
            classification = "ROLLED_BACK_VERIFIED"
        else:
            classification = "RECOVERY_REQUIRED"
    else:
        classification = "RECOVERY_REQUIRED"

    return {
        "classification": classification,
        "journal": str(journal_path.relative_to(root)),
        "transaction_id": journal["transaction_id"],
        "journal_state": state,
        "journal_data": journal,
        "targets": observed_targets,
        "reason": None if classification.endswith("_VERIFIED") else "Journalzustand und Dateihashes ergeben keinen eindeutig sicheren Endzustand.",
    }


def _restore_backups(root: Path, journal: dict) -> None:
    for target in reversed(journal["targets"]):
        backup = root / target["backup_path"]
        destination = root / target["path"]
        if not backup.exists():
            raise FileNotFoundError(f"Backup fehlt: {target['backup_path']}")
        shutil.copy2(backup, destination)
        with destination.open("rb") as handle:
            os.fsync(handle.fileno())
    _fsync_dir(root / "data")


def _persist_normalized_journal(root: Path, journal_path: Path, journal: dict, state: str, note: str | None = None) -> None:
    updated = dict(journal)
    updated["state"] = state
    updated["updated_at"] = _utc_now()
    if note:
        previous = updated.get("error")
        updated["error"] = f"{previous} | {note}" if previous else note
    _write_fsync(journal_path, updated)


def create_commit_evidence(root: Path, classification: dict) -> dict:
    if classification["classification"] not in {"COMMITTED_VERIFIED", "ROLLED_BACK_VERIFIED"}:
        raise ValueError("Evidence darf nur für verifizierte Endzustände erzeugt werden.")

    journal = classification["journal_data"]
    targets = classification["targets"]
    evidence = {
        "schema_version": "1.0",
        "evidence_id": f"EVID-{journal['transaction_id']}",
        "transaction_id": journal["transaction_id"],
        "candidate_id": journal["candidate_id"],
        "intent_id": journal["intent_id"],
        "classification": classification["classification"],
        "journal_state_observed": classification["journal_state"],
        "verified_at": _utc_now(),
        "journal_hash": sha256_json(journal),
        "before_state_hash": _state_hash(targets, "before_hash"),
        "after_state_hash": _state_hash(targets, "after_hash"),
        "targets": [
            {
                "path": target["path"],
                "before_hash": target["before_hash"],
                "after_hash": target["after_hash"],
                "observed_hash": target["observed_hash"],
            }
            for target in targets
        ],
    }
    evidence["evidence_hash"] = sha256_json(evidence)

    path = root / "evidence" / "transactions" / f"{journal['transaction_id']}.json"
    if path.exists():
        existing = _load(path)
        return {"path": str(path.relative_to(root)), "evidence": existing, "created": False}
    _write_fsync(path, evidence, exclusive=True)
    return {"path": str(path.relative_to(root)), "evidence": evidence, "created": True}


def replay_journal(root: Path, journal_path: Path, *, repair: bool = False) -> dict:
    classification = classify_journal(root, journal_path)
    if classification["classification"] in {"CORRUPT_JOURNAL", "HASH_MISMATCH"}:
        return classification

    if classification["classification"] == "RECOVERY_REQUIRED" and repair:
        journal = classification.get("journal_data") or _load(journal_path)
        try:
            _restore_backups(root, journal)
            _persist_normalized_journal(root, journal_path, journal, "ROLLED_BACK", "Recovery Replay stellte den Vorher-Zustand aus Backups wieder her.")
        except Exception as exc:
            return {
                "classification": "RECOVERY_REQUIRED",
                "journal": str(journal_path.relative_to(root)),
                "transaction_id": journal.get("transaction_id"),
                "reason": f"Recovery fehlgeschlagen: {type(exc).__name__}: {exc}",
            }
        classification = classify_journal(root, journal_path)

    if classification["classification"] in {"COMMITTED_VERIFIED", "ROLLED_BACK_VERIFIED"}:
        if repair:
            expected_state = "COMMITTED" if classification["classification"] == "COMMITTED_VERIFIED" else "ROLLED_BACK"
            if classification["journal_state"] != expected_state:
                _persist_normalized_journal(root, journal_path, classification["journal_data"], expected_state, "Recovery Replay normalisierte einen hashverifizierten Endzustand.")
                classification = classify_journal(root, journal_path)
        evidence = create_commit_evidence(root, classification)
        return {
            "classification": classification["classification"],
            "transaction_id": classification["transaction_id"],
            "journal": classification["journal"],
            "evidence": evidence["path"],
            "evidence_created": evidence["created"],
            "reason": None,
        }

    return classification


def replay_all(root: Path, *, repair: bool = False) -> dict:
    recovery = root / "recovery"
    journals = sorted(recovery.glob("TX-*.json")) if recovery.exists() else []
    if not journals:
        return {"result": "CLEAN", "counts": {}, "items": []}

    items = [replay_journal(root, journal_path, repair=repair) for journal_path in journals]
    counts: dict[str, int] = {}
    for item in items:
        key = item["classification"]
        counts[key] = counts.get(key, 0) + 1

    blocking = {"CORRUPT_JOURNAL", "HASH_MISMATCH", "RECOVERY_REQUIRED"}
    result = "BLOCKED" if any(key in counts for key in blocking) else "PASS"
    return {"result": result, "counts": counts, "items": items}


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministischer Recovery-Replay für PROVOWARE-Wissenstransaktionen.")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--repair", action="store_true", help="Unvollständige Mischzustände aus vorhandenen Backups auf den Vorher-Zustand zurückrollen.")
    args = parser.parse_args()

    result = replay_all(Path(args.root).resolve(), repair=args.repair)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["result"] in {"PASS", "CLEAN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
