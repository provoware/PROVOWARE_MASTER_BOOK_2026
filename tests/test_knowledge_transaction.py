from __future__ import annotations

from pathlib import Path
import copy
import json
import shutil
import tempfile

import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import acceptance_preview
import preflight as preflight_module
from canonical_json import sha256_json
from knowledge_transaction import execute_transaction


DATA_FILES = (
    "masterbook_seed.json",
    "knowledge-deltas.json",
    "inbox.json",
    "categories.json",
    "relationship-types.json",
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_root(base: Path) -> Path:
    root = base / "fixture"
    (root / "data").mkdir(parents=True)
    for name in DATA_FILES:
        shutil.copy2(ROOT / "data" / name, root / "data" / name)
    return root


def hashes(root: Path) -> dict[str, str]:
    result = {}
    for name in ("masterbook_seed.json", "knowledge-deltas.json", "inbox.json"):
        result[name] = sha256_json(load(root / "data" / name))
    return result


def make_intent(root: Path, candidate_id: str = "INBOX-001") -> dict:
    old_preflight_root = preflight_module.ROOT
    old_preview_root = acceptance_preview.ROOT
    try:
        preflight_module.ROOT = root
        acceptance_preview.ROOT = root
        seed = load(root / "data/masterbook_seed.json")
        inbox = load(root / "data/inbox.json")["items"]
        candidate = next(item for item in inbox if item["candidate_id"] == candidate_id)
        preview = acceptance_preview.build_preview(candidate, seed, plan_number=1)
        if preview["result"] != "PREVIEW_READY":
            return {"intent_id":"INTENT-TEST","status":"BLOCKED"}
        return {
            "intent_id":"INTENT-TEST",
            "status":"COMMIT_READY",
            "target_entry_id":preview["after"]["id"],
            "target_hash":preview["after_hash"],
        }
    finally:
        preflight_module.ROOT = old_preflight_root
        acceptance_preview.ROOT = old_preview_root


def run_with_roots(root: Path, intent: dict, fault_at: str | None = None):
    old_preflight_root = preflight_module.ROOT
    old_preview_root = acceptance_preview.ROOT
    try:
        preflight_module.ROOT = root
        acceptance_preview.ROOT = root
        return execute_transaction(root, "INBOX-001", intent, fault_at=fault_at)
    finally:
        preflight_module.ROOT = old_preflight_root
        acceptance_preview.ROOT = old_preview_root


def test_success() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = fixture_root(Path(temp))
        before_seed = load(root / "data/masterbook_seed.json")
        before_delta = load(root / "data/knowledge-deltas.json")
        intent = make_intent(root)
        result = run_with_roots(root, intent)
        assert result["result"] == "COMMITTED", result

        seed = load(root / "data/masterbook_seed.json")
        inbox = load(root / "data/inbox.json")
        deltas = load(root / "data/knowledge-deltas.json")
        assert len(seed) == len(before_seed) + 1
        assert len(deltas["items"]) == len(before_delta["items"]) + 1
        accepted = next(i for i in inbox["items"] if i["candidate_id"] == "INBOX-001")
        assert accepted["status"] == "uebernommen"
        assert accepted["accepted_entry_id"] == result["entry_id"]
        journal = load(root / result["journal"])
        assert journal["state"] == "COMMITTED"
        assert set(journal["applied_files"]) == {
            "data/masterbook_seed.json",
            "data/knowledge-deltas.json",
            "data/inbox.json",
        }


def test_fault_matrix_rolls_back() -> None:
    fault_points = [
        "after_prepare",
        "before_replace_1", "after_replace_1",
        "before_replace_2", "after_replace_2",
        "before_replace_3", "after_replace_3",
        "before_validation",
    ]
    for fault_at in fault_points:
        with tempfile.TemporaryDirectory() as temp:
            root = fixture_root(Path(temp))
            before = hashes(root)
            intent = make_intent(root)
            result = run_with_roots(root, intent, fault_at=fault_at)
            assert result["result"] == "ROLLED_BACK", (fault_at, result)
            assert hashes(root) == before, fault_at
            journal = load(root / "recovery" / f"{result['transaction_id']}.json")
            assert journal["state"] == "ROLLED_BACK", fault_at


def test_non_ready_candidate_cannot_commit() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = fixture_root(Path(temp))
        before = hashes(root)
        blocked = make_intent(root, "INBOX-002")
        assert blocked["status"] == "BLOCKED"
        result = execute_transaction(root, "INBOX-002", blocked)
        assert result["result"] == "BLOCKED"
        assert hashes(root) == before


if __name__ == "__main__":
    test_success()
    test_fault_matrix_rolls_back()
    test_non_ready_candidate_cannot_commit()
    print("PASS: Knowledge Transaction Commit + 8 Fault-Injection-Punkte + Non-READY-Blockade geprüft.")
