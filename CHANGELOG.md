# Änderungsprotokoll

## 0.1.2-i003 – 2026-08-09

### Hinzugefügt

- lokale, nur lesende Wissenseingangs-Ansicht
- vier deterministische Demonstrationskandidaten für `READY`, `DUPLICATE`, `CONFLICT` und `BLOCKED`
- sichtbare Begründung jedes Preflight-Zustands
- Tastaturbedienung der Inbox-Karten
- Statuskennzeichnung zusätzlich über Text und Symbol, nicht nur Farbe
- Browser-Derivat `src/inbox.js` für direkten Offline-Start per `file://`
- Single-Source-Generator `scripts/generate_inbox.py` von `data/inbox.json` nach `src/inbox.js`

### Geändert

- `index.html` auf Iteration 003 aktualisiert und Wissenseingang in die Navigation aufgenommen
- `src/app.js` um read-only Inbox-Rendering und deterministische Vorprüfung erweitert
- `src/style.css` um zugängliche Statusdarstellung erweitert
- `PROJEKTSTATUS.json` auf Version `0.1.2-i003` und 39 % Fortschritt aktualisiert

### Qualitätsentscheidungen

- `data/inbox.json` ist die kanonische Wissenseingangsquelle; `src/inbox.js` ist nur Browser-Derivat
- weiterhin keine persistente Nutzeränderung
- keine automatische Übernahme von `READY`
- keine automatische Zusammenführung von `DUPLICATE`
- keine automatische Auflösung von `CONFLICT`
- `BLOCKED` bleibt sichtbar blockiert
- Laufzeit-/Browsertests werden nicht als PASS behauptet, solange sie nicht real ausgeführt wurden

### Nächster Schritt

Iteration 004 – Knowledge-Delta-Vertrag und read-only Änderungsverlauf; erst danach schreibende Inbox-Übernahme.

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
