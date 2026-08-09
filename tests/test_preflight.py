from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.preflight import preflight

seed = json.loads((ROOT / 'data' / 'masterbook_seed.json').read_text(encoding='utf-8'))

base = {
    'candidate_id':'INBOX-001',
    'title':'Neue kleine Beobachtung',
    'summary':'Ein neuer, noch nicht vorhandener Wissenskandidat.',
    'type':'beobachtung',
    'primary_category':'Erfahrungsbuch',
    'categories':['Wissenskonsolidierung'],
    'priority':'P2',
    'maturity':'E0',
    'scope':'projekt',
    'sources':[{'kind':'projektchat','ref':'Test','claim':'Testquelle'}],
    'status':'neu'
}

assert preflight(base, seed)['result'] == 'READY'

duplicate = dict(base, candidate_id='INBOX-002', title=seed[0]['title'])
result = preflight(duplicate, seed)
assert result['result'] == 'DUPLICATE'
assert result['possible_duplicate_of'] == seed[0]['id']

bad_category = dict(base, candidate_id='INBOX-003', primary_category='NICHT_VORHANDEN')
assert preflight(bad_category, seed)['result'] == 'BLOCKED'

false_gold = dict(base, candidate_id='INBOX-004', type='goldene_regel', maturity='E2')
assert preflight(false_gold, seed)['result'] == 'BLOCKED'

conflict = dict(base, candidate_id='INBOX-005', relationships=[{'type':'widerspricht','target_id':'RULE-001'}])
result = preflight(conflict, seed)
assert result['result'] == 'CONFLICT'
assert result['conflict_with'] == ['RULE-001']

print('PASS: READY, DUPLICATE, BLOCKED und CONFLICT deterministisch geprüft.')
