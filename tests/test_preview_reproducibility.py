from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_preview_reproducibility import verify


def test_ready_preview_is_reproducible():
    evidence = verify("INBOX-001")
    assert evidence["result"] == "PASS"
    assert evidence["equal"] is True
    assert evidence["run_a_hash"] == evidence["run_b_hash"]
    assert evidence["plan_hash_a"] == evidence["plan_hash_b"]
    assert evidence["details"]["preview_result"] == "PREVIEW_READY"


def test_unknown_candidate_is_blocked():
    evidence = verify("INBOX-999")
    assert evidence["result"] == "BLOCKED"
    assert evidence["equal"] is False
