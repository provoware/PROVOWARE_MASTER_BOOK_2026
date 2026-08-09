from __future__ import annotations
from pathlib import Path
import json, shutil, tempfile
import acceptance_preview, verify_preview_reproducibility, intent_guard, project_state
from canonical_json import sha256_json
from knowledge_transaction import execute_transaction
from recovery_replay import replay_all

ROOT=Path(__file__).resolve().parents[1]

def _load(p): return json.loads(p.read_text(encoding='utf-8'))

def qualify(candidate_id='INBOX-001'):
    with tempfile.TemporaryDirectory(prefix='provoware-i011-') as td:
        root=Path(td)
        shutil.copytree(ROOT/'data',root/'data')
        for mod in (acceptance_preview,verify_preview_reproducibility,intent_guard,project_state): mod.ROOT=root
        before=sha256_json(_load(root/'data/masterbook_seed.json'))
        preview=verify_preview_reproducibility.verify(candidate_id)
        intent=intent_guard.validate_intent(intent_guard.build_intent(candidate_id))
        tx=execute_transaction(root,candidate_id,intent)
        replay=replay_all(root)
        after=sha256_json(_load(root/'data/masterbook_seed.json'))
        txid=tx.get('transaction_id')
        ep=root/'evidence/transactions'/f'{txid}.json' if txid else None
        evidence=_load(ep) if ep and ep.exists() else None
        checks={'preview_pass':preview.get('result')=='PASS','intent_ready':intent.get('status')=='COMMIT_READY','transaction_committed':tx.get('result')=='COMMITTED','restart_replay_pass':replay.get('result')=='PASS','commit_evidence_present':evidence is not None,'state_changed':before!=after}
        result='SINGLE_COMMIT_QUALIFIED' if all(checks.values()) else 'BLOCKED'
        receipt={'schema_version':'1.0','qualification_id':'QUAL-I011-0001','candidate_id':candidate_id,'result':result,'checks':checks,'before_seed_hash':before,'after_seed_hash':after,'preview_evidence_hash':sha256_json(preview),'intent_hash':sha256_json(intent),'transaction_id':txid,'replay_hash':sha256_json(replay),'commit_evidence_hash':sha256_json(evidence) if evidence else None}
        receipt['receipt_hash']=sha256_json(receipt)
        return receipt

if __name__=='__main__':
    r=qualify(); print(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)); raise SystemExit(0 if r['result']=='SINGLE_COMMIT_QUALIFIED' else 2)
