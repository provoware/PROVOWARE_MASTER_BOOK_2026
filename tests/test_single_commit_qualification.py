from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from single_commit_qualification import qualify

def test_single_commit_chain_isolated_and_complete():
    before=(ROOT/'data/masterbook_seed.json').read_bytes()
    receipt=qualify('INBOX-001')
    assert receipt['result']=='SINGLE_COMMIT_QUALIFIED'
    assert all(receipt['checks'].values())
    assert receipt['transaction_id']
    assert receipt['commit_evidence_hash']
    assert receipt['before_seed_hash']!=receipt['after_seed_hash']
    assert (ROOT/'data/masterbook_seed.json').read_bytes()==before

def test_non_ready_candidate_blocks():
    receipt=qualify('INBOX-004')
    assert receipt['result']=='BLOCKED'
    assert receipt['checks']['transaction_committed'] is False
