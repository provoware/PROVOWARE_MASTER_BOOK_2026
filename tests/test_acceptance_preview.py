from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from acceptance_preview import build_preview
from canonical_json import sha256_json


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> int:
    seed = load("data/masterbook_seed.json")
    inbox = load("data/inbox.json")["items"]
    by_id = {item["candidate_id"]: item for item in inbox}

    ready_a = build_preview(by_id["INBOX-001"], seed)
    ready_b = build_preview(by_id["INBOX-001"], seed)
    assert ready_a == ready_b, "Vorschau ist nicht deterministisch"
    assert ready_a["result"] == "PREVIEW_READY"
    assert ready_a["operation"] == "create"
    assert ready_a["before"] is None
    assert ready_a["after_hash"] == sha256_json(ready_a["after"])
    assert ready_a["delta_preview"]["after_hash"] == ready_a["after_hash"]
    assert ready_a["undo_preview"]["operation"] == "delete_created_entry"

    for candidate_id in ("INBOX-002", "INBOX-003", "INBOX-004"):
        preview = build_preview(by_id[candidate_id], seed)
        assert preview["result"] == "PREVIEW_BLOCKED", candidate_id
        assert preview["operation"] == "blocked", candidate_id
        assert preview["after"] is None, candidate_id
        assert preview["after_hash"] is None, candidate_id
        assert preview["undo_preview"]["status"] == "NOT_APPLICABLE", candidate_id

    print("PASS: deterministische READY-Vorschau; DUPLICATE/CONFLICT/BLOCKED erzeugen keinen Create-Plan.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
