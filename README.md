# PROVOWARE Knowledge & Project Intelligence

Lokaler Wissensspeicher, Masterbuch und spätere Standards Engine für projektübergreifendes Entwicklungswissen.

## Aktueller Stand – Iteration 004

Enthalten:

- `PROJEKTSTATUS.json`
- Knowledge Core Contract v1
- Navigation Contract v1
- maschinenlesbares Wissenseintrag-Schema
- zentrale Kategorien und Beziehungstypen
- versionierter Wissenseingang mit deterministischem Preflight
- kanonischer Masterbuch-Bestand in `data/masterbook_seed.json`
- read-only Knowledge-Inbox
- Knowledge-Delta-Vertrag und kanonisches Ledger `data/knowledge-deltas.json`
- read-only Ansicht `Was hat sich geändert?`
- Single-Source-Generatoren für Browser-Derivate
- Smoke-, Preflight- und Delta-Vertragstests

## Start

`index.html` lokal in Chrome oder Firefox öffnen.

Die Oberfläche bleibt absichtlich lesend. Persistente Nutzdatenspeicherung und schreibende Inbox-Übernahme werden erst nach stabilem Delta-/Undo-Vertrag eingeführt.

## Entwicklerprüfung

```bash
python3 scripts/generate_seed.py
python3 scripts/generate_inbox.py
python3 scripts/generate_deltas.py
python3 tests/smoke.py
python3 tests/test_preflight.py
python3 tests/test_deltas.py
```

Nicht ausgeführte Prüfungen dürfen nicht als PASS interpretiert werden.

## Nächster Schritt

Iteration 005: reversible Inbox-Übernahme zunächst als Preview/Simulation mit Delta-Erzeugung und Undo-Vertrag; kein stilles Schreiben in den kanonischen Bestand.
