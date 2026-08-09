# Iteration 002 – Taxonomie, Beziehungen und Wissenseingang

## Ziel

Den bislang offenen Übergang zwischen Roh-Erkenntnis und kanonischem Masterbuch kontrolliert schließen, ohne bereits persistente UI-Schreiblogik oder KI-Entscheidungen vorwegzunehmen.

## Umgesetzt

- zentrale Kategorienregistry in `data/categories.json`
- zentrale Beziehungsregistry in `data/relationship-types.json`
- leerer, versionierter Wissenseingang in `data/inbox.json`
- Schema für Wissenseingangs-Kandidaten
- deterministischer Preflight mit vier Ergebnissen: `READY`, `DUPLICATE`, `CONFLICT`, `BLOCKED`
- Generator `scripts/generate_seed.py`; `data/masterbook_seed.json` bleibt die kanonische Quelle für den Browser-Seed
- Regressionstests für die vier Preflight-Pfade

## Sicherheitsgrenzen

Der Preflight führt keine semantische KI-Zusammenführung durch. Er erkennt nur deterministisch prüfbare Zustände. Ein Konflikt bleibt sichtbar; eine Dublette wird nicht automatisch verschmolzen. Goldene Regeln benötigen weiterhin E5.

## Rückfallfähigkeit

Die Iteration ist additiv. Bestehende Masterbuch-Einträge werden nicht migriert oder gelöscht. Neue Registries und Skripte können entfernt werden, ohne die Iteration-001-Leseansicht unbrauchbar zu machen.

## Validierung

Repository-Schreibvorgänge und Rücklesen der neuen Dateien sind prüfbar. Die ausführbaren Python-Tests sind vorhanden, konnten in dieser Ausführung wegen eines transienten lokalen Ausführungsfehlers jedoch nicht real gestartet werden. Daher wird hierfür ausdrücklich kein PASS behauptet.

## Nächster Schritt

Iteration 003: Preflight in eine rein lokale Knowledge-Inbox-Ansicht integrieren, zunächst weiterhin ohne persistente Nutzeränderung. Kandidaten sollen importiert/angezeigt und mit den Zuständen READY, DUPLICATE, CONFLICT oder BLOCKED dargestellt werden.
