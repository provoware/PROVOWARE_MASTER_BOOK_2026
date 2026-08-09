from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import os
import shutil

from acceptance_preview import build_preview
from canonical_json import canonical_json, sha256_json
from intent_guard import build_intent, validate_intent
from recovery_startup_gate import evaluate_write_gate

ROOT = Path(__file__).resolve().parents[1]
TARGET_PATHS = (
    "data/masterbook_seed.json",
    "data/knowledge-deltas.json",
    "data/inbox.json",
)


class InjectedFault(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_fsync(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (canonical_json(payload) + "\n").encode("utf-8")
    with path.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _fsync_dir(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _maybe_fault(fault_at: str | None, point: str) -> None:
    if fault_at == point:
        raise InjectedFault(point)


def _next_number(items: list[dict], key: str, prefix: str) -> int:
    numbers = []
    for item in items:
        value = item.get(key, "")
        if value.startswith(prefix):
            try:
                numbers.append(int(value.removeprefix(prefix)))
            except ValueError:
                pass
    return max(numbers, default=0) + 1


def build_target_documents(root: Path, candidate_id: str, intent: dict) -> tuple[dict, dict, dict, dict]:
    seed = _load(root / "data/masterbook_seed.json")
    inbox_doc = _load(root / "data/inbox.json")
    delta_doc = _load(root / "data/knowledge-deltas.json")
    candidate = next((item for item in inbox_doc["items"] if item["candidate_id"] == candidate_id), None)
    if candidate is None:
        raise ValueError("Inbox-Kandidat fehlt")

    preview = build_preview(candidate, seed, plan_number=1)
    if preview.get("result") != "PREVIEW_READY":
        raise ValueError("Preview ist nicht freigabefähig")
    if preview["after"]["id"] != intent["target_entry_id"] or preview["after_hash"] != intent["target_hash"]:
        raise ValueError("Preview stimmt nicht mit dem Intent überein")

    new_seed = list(seed)
    new_seed.append(preview["after"])

    inbox_items = []
    for item in inbox_doc["items"]:
        updated = dict(item)
        if updated["candidate_id"] == candidate_id:
            updated["status"] = "uebernommen"
            updated["accepted_entry_id"] = preview["after"]["id"]
        inbox_items.append(updated)
    new_inbox = {**inbox_doc, "items": inbox_items}

    delta_no = _next_number(delta_doc["items"], "event_id", "DELTA-")
    new_delta = {
        "event_id": f"DELTA-{delta_no:04d}",
        "schema_version": "1.0",
        "timestamp": _utc_now(),
        "iteration": 8,
        "entry_id": preview["after"]["id"],
        "change_type": "neu",
        "reason": f"Atomare Übernahme von {candidate_id} hinter gültigem Commit-Intent.",
        "source": {"kind":"projektdatei","ref":f"data/inbox.json#{candidate_id}","claim":"Kandidat wurde nach Preflight, Preview-Evidence und Intent-Guard übernommen."},
        "before_hash": None,
        "after_hash": preview["after_hash"],
        "status": "direkt_nachgewiesen"
    }
    new_deltas = {**delta_doc, "items": [*delta_doc["items"], new_delta]}
    return new_seed, new_deltas, new_inbox, preview


def _journal_path(root: Path, transaction_id: str) -> Path:
    return root / "recovery" / f"{transaction_id}.json"


def _persist_journal(path: Path, journal: dict) -> None:
    journal["updated_at"] = _utc_now()
    _write_fsync(path, journal)
    _fsync_dir(path.parent)


def _rollback(root: Path, journal: dict) -> None:
    for target in reversed(journal["targets"]):
        path = root / target["path"]
        backup = root / target["backup_path"]
        if backup.exists():
            shutil.copy2(backup, path)
            with path.open("rb") as handle:
                os.fsync(handle.fileno())
    _fsync_dir(root / "data")


def execute_transaction(root: Path, candidate_id: str, intent: dict, fault_at: str | None = None) -> dict:
    gate = evaluate_write_gate(root)
    if gate.get("status") != "WRITE_ALLOWED":
        return {
            "result": "BLOCKED",
            "reason": "Recovery Startup Gate blockiert neue Schreibvorgänge.",
            "gate": gate,
        }

    if intent.get("status") != "COMMIT_READY":
        return {"result":"BLOCKED","reason":"Intent ist nicht COMMIT_READY."}

    try:
        new_seed, new_deltas, new_inbox, preview = build_target_documents(root, candidate_id, intent)
    except (KeyError, ValueError) as exc:
        return {"result":"BLOCKED","reason":f"{type(exc).__name__}: {exc}"}

    documents = {
        "data/masterbook_seed.json": new_seed,
        "data/knowledge-deltas.json": new_deltas,
        "data/inbox.json": new_inbox,
    }
    tx_no = _next_number([{"id": p.stem} for p in (root / "recovery").glob("TX-*.json")], "id", "TX-") if (root / "recovery").exists() else 1
    tx_id = f"TX-{tx_no:04d}"
    recovery_dir = root / "recovery" / tx_id
    recovery_dir.mkdir(parents=True, exist_ok=True)

    targets = []
    for relative in TARGET_PATHS:
        source = root / relative
        before = _load(source)
        backup_rel = f"recovery/{tx_id}/{source.name}.bak"
        temp_rel = f"recovery/{tx_id}/{source.name}.tmp"
        backup = root / backup_rel
        temp = root / temp_rel
        shutil.copy2(source, backup)
        _write_fsync(temp, documents[relative])
        targets.append({
            "path": relative,
            "before_hash": sha256_json(before),
            "after_hash": sha256_json(documents[relative]),
            "backup_path": backup_rel,
            "temp_path": temp_rel,
        })

    journal = {
        "schema_version":"1.0",
        "transaction_id":tx_id,
        "candidate_id":candidate_id,
        "intent_id":intent.get("intent_id", "UNKNOWN"),
        "state":"PREPARED",
        "created_at":_utc_now(),
        "updated_at":_utc_now(),
        "targets":targets,
        "applied_files":[],
        "error":None,
    }
    journal_path = _journal_path(root, tx_id)
    _persist_journal(journal_path, journal)

    try:
        _maybe_fault(fault_at, "after_prepare")
        journal["state"] = "WRITING"
        _persist_journal(journal_path, journal)
        for index, target in enumerate(targets, start=1):
            _maybe_fault(fault_at, f"before_replace_{index}")
            os.replace(root / target["temp_path"], root / target["path"])
            _fsync_dir((root / target["path"]).parent)
            journal["applied_files"].append(target["path"])
            _persist_journal(journal_path, journal)
            _maybe_fault(fault_at, f"after_replace_{index}")

        journal["state"] = "VALIDATING"
        _persist_journal(journal_path, journal)
        _maybe_fault(fault_at, "before_validation")
        for target in targets:
            current = _load(root / target["path"])
            if sha256_json(current) != target["after_hash"]:
                raise RuntimeError(f"Hashprüfung fehlgeschlagen: {target['path']}")
        if preview["after"]["id"] not in {entry["id"] for entry in _load(root / "data/masterbook_seed.json")}:
            raise RuntimeError("Zieleintrag fehlt nach dem Schreiben")
        journal["state"] = "COMMITTED"
        _persist_journal(journal_path, journal)
        return {"result":"COMMITTED","transaction_id":tx_id,"entry_id":preview["after"]["id"],"journal":str(journal_path.relative_to(root))}
    except Exception as exc:
        journal["error"] = f"{type(exc).__name__}: {exc}"
        try:
            _rollback(root, journal)
            journal["state"] = "ROLLED_BACK"
            _persist_journal(journal_path, journal)
            return {"result":"ROLLED_BACK","transaction_id":tx_id,"reason":journal["error"]}
        except Exception as rollback_exc:
            journal["state"] = "RECOVERY_REQUIRED"
            journal["error"] += f" | Rollback: {type(rollback_exc).__name__}: {rollback_exc}"
            _persist_journal(journal_path, journal)
            return {"result":"RECOVERY_REQUIRED","transaction_id":tx_id,"reason":journal["error"]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Crash-konsistente Einzelübernahme eines READY-Wissenskandidaten.")
    parser.add_argument("candidate_id", nargs="?", default="INBOX-001")
    parser.add_argument("--fault-at", default=None)
    args = parser.parse_args()

    intent = validate_intent(build_intent(args.candidate_id))
    if intent.get("status") != "COMMIT_READY":
        print(json.dumps({"result":"BLOCKED","intent":intent}, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    result = execute_transaction(ROOT, args.candidate_id, intent, fault_at=args.fault_at)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["result"] == "COMMITTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
