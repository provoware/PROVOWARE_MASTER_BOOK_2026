# Änderungsprotokoll

## 0.1.4-i005 – 2026-08-09

### Hinzugefügt

- `schemas/change-plan.schema.json` für schreibfreie Änderungspläne
- `schemas/undo-record.schema.json` für Undo-Vorschauen
- `scripts/canonical_json.py` für deterministische UTF-8-JSON-Serialisierung und SHA-256
- `scripts/acceptance_preview.py` für reversible READY-Übernahmevorschauen
- `tests/test_acceptance_preview.py` mit READY- und Sperrzuständen
- `preview.html` und `src/preview.js` als lokale Nur-Lesen-Vorschau
- Masterbuch-Regel `RULE-005`: vor dem ersten Wissensschreibvorgang reproduzierbarer Änderungsplan
- `DELTA-0006` für die Einführung der Preview-Sicherheitsregel

### Geändert

- `index.html` auf Iteration 005 aktualisiert und Übernahme-Vorschau verlinkt
- `src/style.css` um zugänglichen Navigationslink erweitert
- `data/masterbook_seed.json` und Browser-Derivat `src/seed.js` synchronisiert
- `data/knowledge-deltas.json` und Browser-Derivat `src/deltas.js` synchronisiert
- `PROJEKTSTATUS.json` auf Version `0.1.4-i005` und 49 % Fortschritt aktualisiert

### Qualitätsentscheidungen

- weiterhin kein kanonischer Wissensschreibvorgang
- nur `READY` darf einen `create`-Previewplan erhalten
- `DUPLICATE`, `CONFLICT` und `BLOCKED` erzeugen `PREVIEW_BLOCKED`
- Hashes werden ausschließlich aus deterministisch serialisierten Daten erzeugt
- Web-Crypto-Ausfall wird sichtbar als BLOCKED angezeigt, nicht durch Ersatzwerte kaschiert
- Laufzeit-/Browsertests werden nicht als PASS behauptet, solange sie nicht real ausgeführt wurden

### Nächster Schritt

Iteration 006 – Preview Evidence Contract und real ausgeführte Reproduzierbarkeitsprüfung; erst danach atomaren Commit-Pfad für genau einen READY-Kandidaten vorbereiten.

## 0.1.3-i004 – 2026-08-09

### Hinzugefügt

- Knowledge-Delta-Vertrag `schemas/knowledge-delta.schema.json`
- kanonisches Delta-Ledger `data/knowledge-deltas.json`
- Single-Source-Generator `scripts/generate_deltas.py`
- Browser-Derivat `src/deltas.js`
- read-only Navigation `Was hat sich geändert?`
- Delta-Detailansicht mit Grund, Quelle, Iteration, Zeitpunkt und Nachweisstatus
- Regressionstest `tests/test_deltas.py`
- Masterbuch-Regel `RULE-004` zur nachvollziehbaren Protokollierung von Wissensänderungen
- Iterationsdokumentation `docs/ITERATION_004.md`

### Geändert

- `index.html` auf Iteration 004 aktualisiert
- `src/app.js` um read-only Änderungsverlauf erweitert
- `README.md` mit Delta-/History-Vertrag synchronisiert
- `PROJEKTSTATUS.json` auf Iteration 004 und 44 % Fortschritt aktualisiert

### Qualitätsentscheidungen

- weiterhin keine schreibende Inbox-Übernahme
- historisch rekonstruierte Delta-Ereignisse werden ausdrücklich so markiert
- fehlende Snapshot-Hashes werden nicht erfunden
- `data/knowledge-deltas.json` ist kanonisch; `src/deltas.js` nur Browser-Derivat
- Laufzeit-/Browsertests bleiben BLOCKED/NOT_RUN, solange sie nicht real ausgeführt wurden

### Nächster Schritt

Iteration 005 – reversible Inbox-Übernahme zunächst als Preview/Simulation mit Delta-Erzeugung und Undo-Vertrag.

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
