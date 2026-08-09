from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from qualification_receipt_gate import run_gate, verify_receipt
from single_commit_qualification import qualify


def test_full_gate_accepts_positive_and_blocks_negative():
    result=run_gate()
    assert result['result']=='PASS'
    assert result['positive']['result']=='QUALIFICATION_ACCEPTED'
    assert result['negative_non_ready_blocked'] is True
    assert result['canonical_history_hash']


def test_tampered_receipt_is_blocked():
    receipt=qualify('INBOX-001')
    receipt['after_seed_hash']='0'*64
    checked=verify_receipt(receipt)
    assert checked['result']=='QUALIFICATION_BLOCKED'
    assert checked['checks']['receipt_hash_valid'] is False
