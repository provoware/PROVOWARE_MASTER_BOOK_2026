# Iteration 004 — Knowledge Delta Contract + read-only Änderungsverlauf

## Ziel

Vor jeder späteren schreibenden Inbox-Übernahme wird zuerst ein nachvollziehbarer Änderungsvertrag eingeführt.

## Umgesetzt

- `schemas/knowledge-delta.schema.json`
- `data/knowledge-deltas.json` als kanonisches Delta-Ledger
- `scripts/generate_deltas.py` als Single-Source-Generator
- `src/deltas.js` als Browser-Derivat
- read-only Ansicht `Was hat sich geändert?`
- Detailansicht mit Ereignis, Grund, Quelle, Iteration, Zeitpunkt und Nachweisstatus
- `tests/test_deltas.py`
- Masterbuch-Regel `RULE-004`

## Sicherheitsentscheidung

Noch keine schreibende Übernahme aus der Inbox. Historisch rekonstruierte Delta-Ereignisse werden ausdrücklich als solche markiert. Fehlende Snapshot-Hashes werden nicht erfunden.

## Delta-Typen

- neu
- verbessert
- zusammengefuehrt
- konflikt
- reife_geaendert
- prioritaet_geaendert
- projektbezug_geaendert
- archiviert

## Abnahme

Statisch prüfbar:

- Delta-Datei vorhanden
- eindeutige Event-IDs
- definierte Delta-Typen
- Quelle je Ereignis
- History-Navigation vorhanden
- Browser-Derivat eingebunden

Laufzeitprüfungen bleiben BLOCKED/NOT_RUN, solange sie nicht real ausgeführt wurden.

## Nächster Schritt

Iteration 005 — erste reversible, lokal simulierte Inbox-Übernahme mit Preview, Delta-Erzeugung und Undo-Entwurf; weiterhin ohne stilles Schreiben in den kanonischen Bestand.
