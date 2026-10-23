from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from qualification_receipt_gate import run_gate, verify_receipt
from single_commit_qualification import qualify
from canonical_json import sha256_json


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


def test_incomplete_inner_checks_are_blocked_even_with_matching_receipt_hash():
    valid = qualify('INBOX-001')
    assert verify_receipt(valid)['result'] == 'QUALIFICATION_ACCEPTED'
    original = valid['checks']
    invalid_sets = (
        {},
        {'preview_pass': True},
        {**original, 'preview_pass': 1},
        {**original, 'additional_check': False},
        None,
        [],
    )
    for inner_checks in invalid_sets:
        altered = {**valid, 'checks': inner_checks}
        altered.pop('receipt_hash')
        altered['receipt_hash'] = sha256_json(altered)
        result = verify_receipt(altered)
        assert result['result'] == 'QUALIFICATION_BLOCKED', inner_checks
        assert result['checks']['all_inner_checks'] is False
        assert result['checks']['receipt_hash_valid'] is True
