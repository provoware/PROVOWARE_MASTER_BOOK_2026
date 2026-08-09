# Iteration 012 – Historical Delta Integrity Repair + Append-only Guard

## Ausgangslage

Iteration 011 hatte beim Ergänzen von `DELTA-0012` ältere Texte in `data/knowledge-deltas.json` unbeabsichtigt verkürzt. Das Browser-Derivat `src/deltas.js` und der Git-Stand aus Iteration 010 enthielten die vollständigen historischen Fassungen von `DELTA-0001` bis `DELTA-0011` weiterhin unverändert. Dadurch war eine quellengebundene, verlustfreie Reparatur möglich.

## Gewählter Schritt

1. vollständige historische Fassungen aus dem letzten unveränderten Git-Stand restaurieren,
2. `DELTA-0012` additiv erhalten,
3. `DELTA-0013` ausschließlich als neue Historienkorrektur/Schutzregel anhängen,
4. kanonisches Ledger und Browser-Derivat synchronisieren,
5. `RULE-012` im Masterbuch ergänzen,
6. Fail-Closed-Append-only-Wächter plus Regressionstest und CI-Gate einführen.

## Sicherheitsvertrag

Bestehende Ereignisse dürfen nicht gelöscht, umgeordnet oder inhaltlich verändert werden. Der Wächter vergleicht den historischen Prefix anhand kanonischer JSON-SHA-256-Werte mit einem früheren Git-Ref. Nur neue Ereignisse am Ende der Historie sind zulässig. Korrekturen an älteren Aussagen werden als neues Delta-Ereignis dokumentiert, nicht durch stilles Umschreiben.

## Artefakte

- `scripts/verify_delta_append_only.py`
- `tests/test_delta_append_only.py`
- `.github/workflows/delta-append-only.yml`
- `data/knowledge-deltas.json`
- `src/deltas.js`
- `data/masterbook_seed.json`
- `src/seed.js`
- `docs/ITERATION_012.md`

## Validierungsstatus

- Git-Historie als Reparaturquelle: PASS
- DELTA-0001 bis DELTA-0011 vollständig gegenüber Iteration 010 restauriert: PASS durch Quellenvergleich
- DELTA-0012 additiv erhalten: PASS_STATIC
- DELTA-0013 angehängt: PASS_STATIC
- kanonisches Ledger und Browser-Derivat synchron: PASS_STATIC
- Masterbuch RULE-012 und Browser-Derivat synchron: PASS_STATIC
- Append-only-Wächter implementiert: PASS_STATIC
- Regressionstest angelegt: CONFIGURED
- CI-Gate angelegt: CONFIGURED
- lokale Python-Ausführung: BLOCKED, da die lokale Umgebung den GitHub-Host nicht auflösen konnte
- GitHub-Actions-Runtime: UNKNOWN_NOT_OBSERVED
- Release-Gate: BLOCKED

## Rückfallfähigkeit

Die Reparatur selbst ist vollständig aus Git-Historie reproduzierbar. Der letzte unveränderte Ausgangsstand für DELTA-0001 bis DELTA-0011 ist Commit `5a23354605b38c4be982ca49018dcc238b53a4f3`. Jede neue Historienänderung ist weiterhin über Git rücksetzbar.

## Nächster Schritt

Iteration 013 – Qualification Receipt Gate + negative Recovery-Block-Qualifikation real ausführbar machen und den zusammenhängenden Einzelcommit-Pfad erstmals mit beobachtetem Runtime-Ergebnis qualifizieren. Keine allgemeine Schreiboberfläche freigeben, solange dieses Gate nicht beobachtet grün ist.
