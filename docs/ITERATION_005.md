# Iteration 005 – Reversible Inbox-Übernahmevorschau

## Ziel

Vor dem ersten echten Wissensschreibvorgang muss aus einem `READY`-Kandidaten reproduzierbar ein unverändernder Änderungsplan entstehen. Der Plan zeigt Zielzustand, SHA-256, Delta-Vorschau und Undo-Vorschau. Kein kanonischer Datensatz wird verändert.

## Ablauf

1. Kandidat aus `data/inbox.json` laden.
2. Bestehenden deterministischen Preflight ausführen.
3. Nur `READY` darf einen `create`-Plan erhalten.
4. Ziel-ID deterministisch aus Typ und vorhandenem Bestand ableiten.
5. Zielobjekt stabil serialisieren.
6. SHA-256 über die kanonische UTF-8-Darstellung bilden.
7. Delta-Vorschau erzeugen.
8. Undo-Vorschau erzeugen.
9. Plan ausschließlich anzeigen oder als stdout ausgeben.

## Sicherheitsregeln

- `DUPLICATE`, `CONFLICT` und `BLOCKED` erzeugen keinen Zielzustand.
- Kein Previewpfad schreibt in `masterbook_seed.json`, `inbox.json` oder `knowledge-deltas.json`.
- Fehlende Hashfähigkeit wird als BLOCKED sichtbar, niemals durch erfundene Werte ersetzt.
- Ein Preview ist noch keine Freigabe zum Commit.
- E5 wird durch die Preview nicht automatisch vergeben.

## Neue Verträge

- `schemas/change-plan.schema.json`
- `schemas/undo-record.schema.json`
- `scripts/canonical_json.py`
- `scripts/acceptance_preview.py`
- `tests/test_acceptance_preview.py`
- `preview.html`
- `src/preview.js`

## Masterbuch-Rückkopplung

`RULE-005` hält als E2/P0-Regel fest, dass vor dem ersten Wissensschreibvorgang ein reproduzierbarer Änderungsplan mit Undo-Information vorhanden sein muss. Die Reife bleibt bewusst E2, da der reale Commit-/Recoverypfad noch nicht praktisch bestätigt wurde.

## Validierung

Statisch geprüft bzw. über Repository-Rücklesen belegbar:

- Schemata angelegt
- Preview-Implementierungen angelegt
- Hauptnavigation auf Iteration 005 synchronisiert
- Masterbuch und Delta-Ledger synchronisiert
- Projektstatus und Changelog synchronisiert

Nicht als PASS gewertet:

- `python3 tests/test_acceptance_preview.py`: BLOCKED, Laufzeitwerkzeug in dieser Ausführung nicht verfügbar
- Chrome-E2E: NOT_RUN
- Firefox-E2E: NOT_RUN
- Release-Gate: BLOCKED

## Rückfall

Die Iteration führt keine Datenmigration und keinen kanonischen Wissensschreibvorgang aus. Rückfall bedeutet ausschließlich das Entfernen der additiven Preview-Dateien und das Zurücksetzen der synchronisierten Metadaten auf Iteration 004.

## Nächster Schritt

Iteration 006 – Preview Evidence Contract: dieselbe READY-Vorschau mehrfach real ausführen, identischen Zielzustand und identischen SHA-256 nachweisen und diesen Nachweis maschinenlesbar speichern. Erst danach darf ein atomarer Commit-Pfad für genau einen READY-Kandidaten vorbereitet werden.
