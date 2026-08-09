# Änderungsprotokoll

## 0.1.1-i002 – 2026-08-09

### Hinzugefügt

- zentrale Taxonomie-Registry `data/categories.json`
- zentrale Beziehungstyp-Registry `data/relationship-types.json`
- versionierter Wissenseingang `data/inbox.json`
- Schema `schemas/inbox-candidate.schema.json`
- deterministischer Preflight mit `READY`, `DUPLICATE`, `CONFLICT`, `BLOCKED`
- Single-Source-Generator `scripts/generate_seed.py`
- Preflight-Regressionstests
- Iterationsdokumentation `docs/ITERATION_002.md`

### Qualitätsentscheidungen

- keine semantische KI-Zusammenführung
- keine automatische Konfliktauflösung
- keine automatische E5-Hochstufung
- `masterbook_seed.json` bleibt kanonische Wissensquelle; `seed.js` ist nur Browser-Derivat
- ausführbare Laufzeittests bleiben BLOCKED, solange sie nicht real gelaufen sind

### Nächster Schritt

Iteration 003 – lokale Knowledge-Inbox-Ansicht mit sichtbaren Preflight-Zuständen, weiterhin ohne persistente Nutzeränderung.

## 0.1.0-i001 – 2026-08-09

### Hinzugefügt

- maschinenlesbare Projektidentität über `PROJEKTSTATUS.json`
- Knowledge Core Contract v1
- Navigation Contract v1
- JSON-Schema für Wissenseinträge
- fünf initiale quellengebundene Masterbuch-Einträge
- lesender Offline-Prototyp mit Suche, Filtern und Detailansicht
- deterministischer Smoke-Test

### Qualitätsentscheidungen

- keine persistente Nutzdatenspeicherung vorgezogen
- keine automatische E5-Hochstufung
- unbekannt, blockiert oder nicht ausgeführt wird nicht als PASS gewertet
- Iteration bleibt additiv und ohne Datenmigration
