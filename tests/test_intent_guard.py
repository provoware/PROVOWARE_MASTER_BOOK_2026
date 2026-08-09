from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from intent_guard import build_intent, validate_intent


def main() -> int:
    now = datetime(2026, 8, 9, 11, 0, tzinfo=timezone.utc)

    ready = build_intent("INBOX-001", now=now)
    assert ready["status"] == "COMMIT_READY"
    assert ready["target_entry_id"]
    assert ready["target_hash"].startswith("sha256:")
    assert ready["undo_plan_hash"].startswith("sha256:")

    validated = validate_intent(ready, now=now + timedelta(minutes=1))
    assert validated["status"] == "COMMIT_READY"

    duplicate = build_intent("INBOX-002", now=now)
    assert duplicate["status"] == "BLOCKED"

    expired = validate_intent(ready, now=now + timedelta(hours=1))
    assert expired["status"] == "STALE"

    tampered_state = dict(ready)
    tampered_state["expected_project_state_hash"] = "sha256:" + "0" * 64
    stale = validate_intent(tampered_state, now=now + timedelta(minutes=1))
    assert stale["status"] == "STALE"

    tampered_target = dict(ready)
    tampered_target["target_hash"] = "sha256:" + "0" * 64
    stale_target = validate_intent(tampered_target, now=now + timedelta(minutes=1))
    assert stale_target["status"] == "STALE"

    print("PASS: Commit-Intent ist an Evidence, Projektzustand, Ziel und Undo gebunden; stale/blocked Pfade geprüft.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
