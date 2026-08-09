# Knowledge Core Contract v1

**Projekt:** PROVOWARE Knowledge & Project Intelligence  
**Iteration:** 001  
**Stand:** 2026-08-09

## Zweck

Dieser Vertrag friert den kleinsten stabilen Wissenskern ein, auf dem Masterbuch und Tool gemeinsam weiterentwickelt werden.

## Invarianten

1. Ein kanonischer Eintrag wird genau einmal gespeichert.
2. Mehrfachsichtbarkeit entsteht über Facetten und Beziehungen, nicht über Datenkopien.
3. Jeder belastbare Eintrag besitzt mindestens eine nachvollziehbare Quelle.
4. Reife `E0–E5` und Priorität `P0–P3` sind voneinander unabhängig.
5. `E5` darf nicht automatisch allein aus Häufigkeit, Priorität oder Wiederholung entstehen.
6. Widersprüche werden explizit als Konflikt modelliert und nicht still aufgelöst.
7. Unbekannt, blockiert oder nicht ausgeführt ist niemals gleich PASS.
8. Historische Revisionen dürfen nicht still überschrieben werden.
9. Automatische Empfehlungen müssen ihre Regel- und Datenbasis erklären können.
10. Sichtbare Bezeichnungen bleiben deutsch; technische Schlüssel bleiben stabil und maschinenlesbar.

## Reife

- E0 – Beobachtung
- E1 – plausible Erkenntnis
- E2 – reproduziert
- E3 – projektübergreifend bestätigt
- E4 – Standard
- E5 – Goldene Regel

## Priorität

- P0 – kritisch
- P1 – hoch
- P2 – normal
- P3 – optional

## Definition of Done für einen Wissenseintrag

- eindeutige ID
- Typ und Titel
- Hauptkategorie
- Reife und Priorität
- Gültigkeitsbereich
- mindestens eine Quelle
- Status und Revision
- Dublettenprüfung möglich
- Konflikte nicht verdeckt
