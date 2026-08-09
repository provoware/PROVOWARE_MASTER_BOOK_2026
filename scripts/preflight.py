from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def _norm(value: str) -> str:
    value = unicodedata.normalize('NFKC', value).casefold().strip()
    return re.sub(r'\s+', ' ', value)


def registries():
    categories = _load(ROOT / 'data' / 'categories.json')['categories']
    relations = _load(ROOT / 'data' / 'relationship-types.json')['relationship_types']
    return {c['label'] for c in categories} | {c['id'] for c in categories}, {r['id'] for r in relations}


def preflight(candidate: dict, seed: list[dict]) -> dict:
    category_ids, relation_ids = registries()
    errors: list[str] = []
    warnings: list[str] = []

    required = {'candidate_id','title','summary','type','primary_category','categories','priority','maturity','scope','sources','status'}
    missing = sorted(required - set(candidate))
    if missing:
        errors.append('Pflichtfelder fehlen: ' + ', '.join(missing))

    if candidate.get('primary_category') not in category_ids:
        errors.append('Unbekannte Hauptkategorie')
    for category in candidate.get('categories', []):
        if category not in category_ids:
            errors.append(f'Unbekannte Kategorie: {category}')

    for rel in candidate.get('relationships', []):
        if rel.get('type') not in relation_ids:
            errors.append(f"Unbekannter Beziehungstyp: {rel.get('type')}")

    if candidate.get('type') == 'goldene_regel' and candidate.get('maturity') != 'E5':
        errors.append('Goldene Regel erfordert E5')

    if not candidate.get('sources'):
        errors.append('Mindestens eine Quelle ist erforderlich')

    duplicate = None
    title_key = _norm(candidate.get('title', ''))
    summary_key = _norm(candidate.get('summary', ''))
    for entry in seed:
        if title_key and _norm(entry.get('title', '')) == title_key:
            duplicate = entry['id']
            break
        if title_key and summary_key and _norm(entry.get('title', '')) == title_key and _norm(entry.get('summary', '')) == summary_key:
            duplicate = entry['id']
            break

    conflicts = []
    for rel in candidate.get('relationships', []):
        if rel.get('type') == 'widerspricht' and rel.get('target_id'):
            conflicts.append(rel['target_id'])

    if errors:
        status = 'BLOCKED'
    elif conflicts:
        status = 'CONFLICT'
    elif duplicate:
        status = 'DUPLICATE'
    else:
        status = 'READY'

    return {
        'result': status,
        'errors': errors,
        'warnings': warnings,
        'possible_duplicate_of': duplicate,
        'conflict_with': conflicts,
        'candidate_id': candidate.get('candidate_id')
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Deterministische Vorprüfung eines Wissenseingangs-Kandidaten.')
    parser.add_argument('candidate', type=Path)
    args = parser.parse_args()
    candidate = _load(args.candidate)
    seed = _load(ROOT / 'data' / 'masterbook_seed.json')
    result = preflight(candidate, seed)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['result'] == 'BLOCKED' else 0


if __name__ == '__main__':
    raise SystemExit(main())
