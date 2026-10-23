from __future__ import annotations
from pathlib import Path
import json
from canonical_json import sha256_json
from single_commit_qualification import qualify

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / 'data' / 'knowledge-deltas.json'
REQUIRED_INNER_CHECKS = (
    'preview_pass', 'intent_ready', 'transaction_committed',
    'restart_replay_pass', 'commit_evidence_present', 'state_changed',
)


def canonical_history_hash() -> str:
    return sha256_json(json.loads(HISTORY.read_text(encoding='utf-8')))


def verify_receipt(receipt: dict) -> dict:
    required = ('before_seed_hash','after_seed_hash','preview_evidence_hash','intent_hash','transaction_id','replay_hash','commit_evidence_hash','receipt_hash')
    inner_checks = receipt.get('checks')
    checks = {
        'qualified_result': receipt.get('result') == 'SINGLE_COMMIT_QUALIFIED',
        'all_inner_checks': (
            isinstance(inner_checks, dict)
            and all(inner_checks.get(key) is True for key in REQUIRED_INNER_CHECKS)
            and all(value is True for value in inner_checks.values())
        ),
        'required_lineage_present': all(bool(receipt.get(k)) for k in required[:-1]),
    }
    unsigned = dict(receipt)
    supplied = unsigned.pop('receipt_hash', None)
    checks['receipt_hash_valid'] = bool(supplied) and sha256_json(unsigned) == supplied
    result = 'QUALIFICATION_ACCEPTED' if all(checks.values()) else 'QUALIFICATION_BLOCKED'
    return {'schema_version':'1.0','result':result,'checks':checks,'canonical_history_hash':canonical_history_hash(),'qualification_receipt_hash':supplied}


def run_gate() -> dict:
    positive = qualify('INBOX-001')
    negative = qualify('INBOX-004')
    positive_gate = verify_receipt(positive)
    negative_blocked = negative.get('result') == 'BLOCKED' and not negative.get('checks', {}).get('transaction_committed', False)
    result = 'PASS' if positive_gate['result'] == 'QUALIFICATION_ACCEPTED' and negative_blocked else 'BLOCKED'
    out = {'schema_version':'1.0','result':result,'positive':positive_gate,'negative_non_ready_blocked':negative_blocked,'canonical_history_hash':canonical_history_hash()}
    out['gate_hash'] = sha256_json(out)
    return out

if __name__ == '__main__':
    result = run_gate()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if result['result'] == 'PASS' else 2)
