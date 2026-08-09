# Iteration 003 – Knowledge-Inbox-Ansicht

**Version:** 0.1.2-i003  
**Stand:** 2026-08-09

## Ziel

Die in Iteration 002 eingeführten Preflight-Zustände werden erstmals in der lokalen Oberfläche sichtbar und verständlich dargestellt, ohne bereits persistente Übernahmefunktionen einzubauen.

## Ausgangsrisiko

Eine schreibende Übernahme vor sichtbarer und nachvollziehbarer Zustandsdarstellung würde Datenmodell, Konfliktlogik und Nutzerführung gleichzeitig verändern. Deshalb bleibt diese Iteration rein lesend und vollständig reversibel.

## Umgesetzt

- Navigationseintrag `Wissenseingang`
- vier reproduzierbare Beispielkandidaten
- sichtbare Zustände `READY`, `DUPLICATE`, `CONFLICT`, `BLOCKED`
- deterministische Browser-Vorprüfung für die vier Basisfälle
- Detailansicht mit Begründung und empfohlenem nächsten Umgang
- Tastaturöffnung über Enter/Leertaste
- Status zusätzlich als Text und Symbol
- keine Übernehmen-, Zusammenführen- oder Konfliktauflösen-Aktion

## Testkandidaten

| Kandidat | erwarteter Zustand | Zweck |
|---|---|---|
| INBOX-001 | READY | valider neuer Kandidat |
| INBOX-002 | DUPLICATE | exakter Titel bereits im Masterbuch |
| INBOX-003 | CONFLICT | explizite `widerspricht`-Beziehung zu RULE-002 |
| INBOX-004 | BLOCKED | Goldene Regel mit Reife E1 statt E5 |

## Datenverlustschutz

Die Oberfläche schreibt keine Nutzdaten. `data/inbox.json` enthält nur kontrollierte Demonstrationskandidaten. Bestehende Masterbuch-Einträge werden weder verändert noch migriert.

## Validierungsstatus

- GitHub-Schreibvorgänge: PASS
- Repository-Rücklesen: PASS nach gezielter Nachprüfung
- statischer Inbox-Vertrag: PASS
- Abdeckung aller vier Preflight-Grundzustände: PASS
- Python-Laufzeittests: BLOCKED
- Chrome-E2E: NOT_RUN
- Firefox-E2E: NOT_RUN
- Release-Gate: BLOCKED

`BLOCKED` und `NOT_RUN` werden ausdrücklich nicht als PASS interpretiert.

## Nächster Schritt

Iteration 004: maschinenlesbaren Knowledge-Delta-Vertrag und eine nur lesende Änderungsverlaufsansicht einführen. Erst danach soll die erste schreibende Inbox-Übernahme geplant werden.
