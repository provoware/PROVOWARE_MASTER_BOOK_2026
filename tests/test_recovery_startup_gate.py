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
from recovery_startup_gate import evaluate_write_gate

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


def target_hashes(root: Path) -> dict[str, str]:
    return {
        name: sha256_json(load(root / "data" / name))
        for name in ("masterbook_seed.json", "knowledge-deltas.json", "inbox.json")
    }


def make_intent(root: Path) -> dict:
    old_preflight_root = preflight_module.ROOT
    old_preview_root = acceptance_preview.ROOT
    try:
        preflight_module.ROOT = root
        acceptance_preview.ROOT = root
        seed = load(root / "data/masterbook_seed.json")
        candidate = next(item for item in load(root / "data/inbox.json")["items"] if item["candidate_id"] == "INBOX-001")
        preview = acceptance_preview.build_preview(candidate, seed, plan_number=1)
        assert preview["result"] == "PREVIEW_READY"
        return {
            "intent_id": "INTENT-GATE-TEST",
            "status": "COMMIT_READY",
            "target_entry_id": preview["after"]["id"],
            "target_hash": preview["after_hash"],
        }
    finally:
        preflight_module.ROOT = old_preflight_root
        acceptance_preview.ROOT = old_preview_root


def test_clean_project_allows_write() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = fixture_root(Path(temp))
        gate = evaluate_write_gate(root)
        assert gate["status"] == "WRITE_ALLOWED", gate
        assert gate["checked_journals"] == 0


def test_corrupt_journal_blocks_write_without_modifying_data() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = fixture_root(Path(temp))
        before = target_hashes(root)
        recovery = root / "recovery"
        recovery.mkdir()
        (recovery / "TX-0001.json").write_text("{kaputt", encoding="utf-8")
        gate = evaluate_write_gate(root)
        assert gate["status"] == "WRITE_BLOCKED", gate
        assert gate["blocking_counts"].get("CORRUPT_JOURNAL") == 1
        assert target_hashes(root) == before
        assert not (root / "evidence").exists(), "Startup-Gate darf keine Evidence schreiben."


def test_transaction_cannot_bypass_recovery_gate() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = fixture_root(Path(temp))
        intent = make_intent(root)
        before = target_hashes(root)
        recovery = root / "recovery"
        recovery.mkdir()
        (recovery / "TX-0001.json").write_text("{kaputt", encoding="utf-8")

        old_preflight_root = preflight_module.ROOT
        old_preview_root = acceptance_preview.ROOT
        try:
            preflight_module.ROOT = root
            acceptance_preview.ROOT = root
            result = execute_transaction(root, "INBOX-001", intent)
        finally:
            preflight_module.ROOT = old_preflight_root
            acceptance_preview.ROOT = old_preview_root

        assert result["result"] == "BLOCKED", result
        assert result.get("gate", {}).get("status") == "WRITE_BLOCKED", result
        assert target_hashes(root) == before


if __name__ == "__main__":
    test_clean_project_allows_write()
    test_corrupt_journal_blocks_write_without_modifying_data()
    test_transaction_cannot_bypass_recovery_gate()
    print("PASS: Recovery Startup Gate erlaubt CLEAN, blockiert beschädigte Journale schreibfrei und kann vom Transaktionspfad nicht umgangen werden.")
