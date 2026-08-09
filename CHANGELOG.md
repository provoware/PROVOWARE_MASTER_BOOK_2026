# Änderungsprotokoll

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

### Nächster Schritt

Iteration 002 – Kategorien-, Beziehungs- und Wissenseingangsmodell mit deterministischer Dubletten-Vorprüfung.
