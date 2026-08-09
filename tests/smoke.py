from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
seed = json.loads((ROOT / 'data' / 'masterbook_seed.json').read_text(encoding='utf-8'))

ids = [entry['id'] for entry in seed]
assert len(ids) == len(set(ids)), 'Doppelte IDs im Seed'

required = {'id','type','title','summary','primary_category','categories','tags','projects','priority','maturity','scope','automatable','status','revision','sources'}
for entry in seed:
    assert not (required - set(entry)), f"Pflichtfelder fehlen: {entry.get('id')}"
    assert entry['priority'] in {'P0','P1','P2','P3'}
    assert entry['maturity'] in {'E0','E1','E2','E3','E4','E5'}
    assert entry['sources'], f"Quelle fehlt: {entry['id']}"
    if entry['type'] == 'goldene_regel':
        assert entry['maturity'] == 'E5', f"Goldene Regel ohne E5: {entry['id']}"

rule = next(entry for entry in seed if entry['id'] == 'RULE-001')
assert rule['type'] == 'regel'
assert rule['primary_category'] == 'Tests'
assert 'Release' in rule['categories']
assert rule['priority'] == 'P0'
assert 'PASS' in rule['tags']

html = (ROOT / 'index.html').read_text(encoding='utf-8')
for asset in ['src/style.css', 'src/seed.js', 'src/app.js']:
    assert asset in html
    assert (ROOT / asset).exists(), f"Fehlendes Asset: {asset}"

print(f'PASS: {len(seed)} Wissenseinträge geprüft; IDs, Pflichtfelder, Reife, Priorität, Quellen und Navigation konsistent.')
