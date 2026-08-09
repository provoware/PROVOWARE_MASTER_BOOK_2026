from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import json

from acceptance_preview import build_preview
from canonical_json import sha256_json
from project_state import project_state_hash
from verify_preview_reproducibility import verify

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def evidence_fingerprint(evidence: dict) -> str:
    stable = {
        "candidate_id": evidence.get("candidate_id"),
        "run_a_hash": evidence.get("run_a_hash"),
        "run_b_hash": evidence.get("run_b_hash"),
        "plan_hash_a": evidence.get("plan_hash_a"),
        "plan_hash_b": evidence.get("plan_hash_b"),
        "equal": evidence.get("equal"),
        "result": evidence.get("result"),
        "details": evidence.get("details", {}),
    }
    return sha256_json(stable)


def build_intent(candidate_id: str, ttl_minutes: int = 30, now: datetime | None = None) -> dict:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    evidence = verify(candidate_id)
    state_hash = project_state_hash()
    base = {
        "schema_version": "1.0",
        "intent_id": "INTENT-0001",
        "candidate_id": candidate_id,
        "operation": "create",
        "preview_evidence_hash": evidence_fingerprint(evidence),
        "expected_project_state_hash": state_hash,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=ttl_minutes)).isoformat(),
    }
    if evidence.get("result") != "PASS" or evidence.get("equal") is not True:
        return {**base, "target_entry_id": "BLOCKED-000", "target_hash": "sha256:" + "0" * 64, "undo_plan_hash": "sha256:" + "0" * 64, "status": "BLOCKED"}

    inbox = _load(ROOT / "data" / "inbox.json")["items"]
    seed = _load(ROOT / "data" / "masterbook_seed.json")
    candidate = next(item for item in inbox if item["candidate_id"] == candidate_id)
    preview = build_preview(candidate, seed, plan_number=1)
    return {
        **base,
        "target_entry_id": preview["after"]["id"],
        "target_hash": preview["after_hash"],
        "undo_plan_hash": sha256_json(preview["undo_preview"]),
        "status": "COMMIT_READY" if preview.get("result") == "PREVIEW_READY" else "BLOCKED",
    }


def validate_intent(intent: dict, now: datetime | None = None) -> dict:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    result = dict(intent)
    if intent.get("status") != "COMMIT_READY":
        result.update(status="BLOCKED", validation_reason="Intent war nicht freigabefähig.")
        return result
    if now > _parse_time(intent["expires_at"]):
        result.update(status="STALE", validation_reason="Intent ist abgelaufen.")
        return result
    if project_state_hash() != intent["expected_project_state_hash"]:
        result.update(status="STALE", validation_reason="Projektzustand hat sich seit der Planung verändert.")
        return result
    evidence = verify(intent["candidate_id"])
    if evidence.get("result") != "PASS" or evidence_fingerprint(evidence) != intent["preview_evidence_hash"]:
        result.update(status="STALE", validation_reason="Preview-Evidence stimmt nicht mehr überein.")
        return result
    inbox = _load(ROOT / "data" / "inbox.json")["items"]
    seed = _load(ROOT / "data" / "masterbook_seed.json")
    candidate = next((item for item in inbox if item["candidate_id"] == intent["candidate_id"]), None)
    if candidate is None:
        result.update(status="STALE", validation_reason="Inbox-Kandidat fehlt.")
        return result
    preview = build_preview(candidate, seed, plan_number=1)
    if preview.get("result") != "PREVIEW_READY":
        result.update(status="STALE", validation_reason="Preview ist nicht mehr freigabefähig.")
        return result
    if preview["after"]["id"] != intent["target_entry_id"] or preview["after_hash"] != intent["target_hash"]:
        result.update(status="STALE", validation_reason="Zielzustand hat sich verändert.")
        return result
    if sha256_json(preview["undo_preview"]) != intent["undo_plan_hash"]:
        result.update(status="STALE", validation_reason="Undo-Plan hat sich verändert.")
        return result
    result.update(status="COMMIT_READY", validation_reason="Intent ist aktuell und an den unveränderten Projektzustand gebunden.")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Erzeugt und validiert einen schreibfreien Intent.")
    parser.add_argument("candidate_id", nargs="?", default="INBOX-001")
    args = parser.parse_args()
    validated = validate_intent(build_intent(args.candidate_id))
    print(json.dumps(validated, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if validated["status"] == "COMMIT_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
