# PROVOWARE Knowledge & Project Intelligence

Lokaler Wissensspeicher, Masterbuch und spätere Standards Engine für projektübergreifendes Entwicklungswissen.

## Stand und Nachweise

Das Projektstatusdokument nennt formal Iteration 014; im Repository liegen darüber hinaus neuere Sicherheits- und CI-Nachträge. Der tatsächliche Release-Stand ergibt sich aus [der Release-Pflichtmatrix](docs/RELEASE_PFLICHTMATRIX.md), nicht aus einer Prozentzahl.

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
- gemeinsame, schreibgeschützte Browser-Vorprüfung in beiden Ansichten
- aus kanonischen Registern generierte Browser-Kategorien und Beziehungstypen
- Browser-Preflight-Regressionstest mit positiven und negativen Fällen

## Start

`index.html` lokal in Chrome oder Firefox öffnen.

Die Oberfläche bleibt absichtlich lesend. Persistente Nutzdatenspeicherung und schreibende Inbox-Übernahme werden erst nach stabilem Delta-/Undo-Vertrag eingeführt.

## Entwicklerprüfung

```bash
python3 scripts/generate_seed.py
python3 scripts/generate_inbox.py
python3 scripts/generate_deltas.py
python3 scripts/generate_registries.py
python3 tests/smoke.py
python3 tests/test_preflight.py
python3 tests/test_deltas.py
python3 scripts/verify_browser_derivatives.py
node tests/test_browser_preflight.cjs
```

Nicht ausgeführte Prüfungen dürfen nicht als PASS interpretiert werden.

## Nächster Schritt

Die Browser-Vorprüfung mit dem kanonischen Python-Preflight abgleichen, die GitHub-Prüfketten auf dem Entwicklungszweig nachweisen und anschließend reale Browser-, 800×600- und Skalierungstests ausführen. Schreibende Übernahmen bleiben bis zu vollständig geprüften Transaktions- und Undo-Verträgen gesperrt.
