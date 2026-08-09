from __future__ import annotations

from pathlib import Path
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
from recovery_replay import classify_journal, replay_journal, replay_all

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


def make_intent(root: Path, candidate_id: str = "INBOX-001") -> dict:
    old_preflight_root = preflight_module.ROOT
    old_preview_root = acceptance_preview.ROOT
    try:
        preflight_module.ROOT = root
        acceptance_preview.ROOT = root
        seed = load(root / "data/masterbook_seed.json")
        candidate = next(item for item in load(root / "data/inbox.json")["items"] if item["candidate_id"] == candidate_id)
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


def commit(root: Path, fault_at: str | None = None) -> dict:
    old_preflight_root = preflight_module.ROOT
    old_preview_root = acceptance_preview.ROOT
    try:
        preflight_module.ROOT = root
        acceptance_preview.ROOT = root
        return execute_transaction(root, "INBOX-001", make_intent(root), fault_at=fault_at)
    finally:
        preflight_module.ROOT = old_preflight_root
        acceptance_preview.ROOT = old_preview_root


def test_clean_root() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = fixture_root(Path(temp))
        result = replay_all(root)
        assert result == {"result":"CLEAN","counts":{},"items":[]}


def test_committed_transaction_gets_immutable_evidence() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = fixture_root(Path(temp))
        tx = commit(root)
        assert tx["result"] == "COMMITTED", tx
        journal_path = root / tx["journal"]

        first = replay_journal(root, journal_path)
        assert first["classification"] == "COMMITTED_VERIFIED", first
        evidence_path = root / first["evidence"]
        evidence = load(evidence_path)
        assert evidence["classification"] == "COMMITTED_VERIFIED"
        assert evidence["transaction_id"] == tx["transaction_id"]
        assert len(evidence["evidence_hash"]) == 64

        second = replay_journal(root, journal_path)
        assert second["classification"] == "COMMITTED_VERIFIED"
        assert second["evidence_created"] is False
        assert load(evidence_path) == evidence


def test_existing_rollback_is_verified() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = fixture_root(Path(temp))
        tx = commit(root, fault_at="after_replace_1")
        assert tx["result"] == "ROLLED_BACK", tx
        journal_path = root / "recovery" / f"{tx['transaction_id']}.json"
        replay = replay_journal(root, journal_path)
        assert replay["classification"] == "ROLLED_BACK_VERIFIED", replay


def test_mixed_incomplete_state_repairs_to_before_state() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = fixture_root(Path(temp))
        before = {
            name: sha256_json(load(root / "data" / name))
            for name in ("masterbook_seed.json", "knowledge-deltas.json", "inbox.json")
        }
        tx = commit(root)
        assert tx["result"] == "COMMITTED"
        journal_path = root / tx["journal"]
        journal = load(journal_path)

        first_target = journal["targets"][0]
        shutil.copy2(root / first_target["backup_path"], root / first_target["path"])
        journal["state"] = "WRITING"
        journal_path.write_text(json.dumps(journal, ensure_ascii=False), encoding="utf-8")

        classification = classify_journal(root, journal_path)
        assert classification["classification"] == "RECOVERY_REQUIRED", classification

        repaired = replay_journal(root, journal_path, repair=True)
        assert repaired["classification"] == "ROLLED_BACK_VERIFIED", repaired
        for name, expected in before.items():
            assert sha256_json(load(root / "data" / name)) == expected, name


def test_corrupt_journal_never_passes() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = fixture_root(Path(temp))
        recovery = root / "recovery"
        recovery.mkdir()
        broken = recovery / "TX-9999.json"
        broken.write_text("{broken", encoding="utf-8")
        result = replay_all(root)
        assert result["result"] == "BLOCKED"
        assert result["counts"]["CORRUPT_JOURNAL"] == 1


if __name__ == "__main__":
    test_clean_root()
    test_committed_transaction_gets_immutable_evidence()
    test_existing_rollback_is_verified()
    test_mixed_incomplete_state_repairs_to_before_state()
    test_corrupt_journal_never_passes()
    print("PASS: Recovery Replay, immutable Commit-Evidence, Rollback-Verifikation, Mixed-State-Recovery und Corrupt-Journal-Blockade geprüft.")
