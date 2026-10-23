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

# Der reale INBOX-002-Wortlaut weicht ab, seine Quellenbehauptung ist aber identisch
# mit RULE-002. Der Titelvergleich allein darf die Dublette nicht als READY melden.
same_source = dict(
    base,
    candidate_id='INBOX-SOURCE',
    title='Einmalig speichern, in vielen Ansichten anzeigen',
    type=seed[1]['type'],
    sources=list(seed[1]['sources']),
)
found = preflight(same_source, seed)
assert found['result'] == 'DUPLICATE', found
assert found['possible_duplicate_of'] == seed[1]['id']

# Gleicher Dokumentverweis mit einer ANDEREN Quellenbehauptung ist keine Dublette.
different_claim = dict(
    same_source,
    candidate_id='INBOX-DIFFERENT',
    sources=[{**same_source['sources'][0], 'claim': 'Andere eigenständige Aussage'}],
)
assert preflight(different_claim, seed)['result'] == 'READY'

print('PASS: READY, DUPLICATE, BLOCKED und CONFLICT deterministisch geprüft.')
