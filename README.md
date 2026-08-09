# PROVOWARE Knowledge & Project Intelligence

Lokaler Wissensspeicher, Masterbuch und spätere Standards Engine für projektübergreifendes Entwicklungswissen.

## Aktueller Stand – Iteration 002

Enthalten:

- `PROJEKTSTATUS.json`
- Knowledge Core Contract v1
- Navigation Contract v1
- maschinenlesbares Wissenseintrag-Schema
- zentral registrierte Kategorien und Beziehungstypen
- versionierter Wissenseingang
- deterministische Vorprüfung für neue Wissenskandidaten
- kanonischer Masterbuch-Bestand in `data/masterbook_seed.json`
- Browser-Derivat `src/seed.js`, erzeugbar über `scripts/generate_seed.py`
- lesender Offline-Prototyp mit Suche und Filtern
- Smoke- und Preflight-Tests

## Start

`index.html` lokal in Chrome oder Firefox öffnen.

Die Oberfläche bleibt absichtlich lesend. Persistente Nutzdatenspeicherung wird erst nach Stabilisierung von Wissenseingang, Dubletten- und Konfliktlogik eingeführt.

## Entwicklerprüfung

```bash
python3 scripts/generate_seed.py
python3 tests/smoke.py
python3 tests/test_preflight.py
```

Nicht ausgeführte Prüfungen dürfen nicht als PASS interpretiert werden.

## Nächster Schritt

Iteration 003: lokale Knowledge-Inbox-Ansicht mit sichtbaren Zuständen `READY`, `DUPLICATE`, `CONFLICT` und `BLOCKED`, weiterhin ohne persistente Nutzeränderung.
