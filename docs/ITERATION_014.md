# Iteration 014 — Canonical Synchronization Repair + Browser Derivative Guard

## Ausgangslage
Iteration 013 hatte das Qualification-Receipt-Gate technisch implementiert, aber `RULE-013`, `DELTA-0014` und der zentrale Changelog waren noch nicht vollständig nachgezogen. Gleichzeitig waren `src/seed.js` und `src/deltas.js` nur bis Iteration 012 synchron. Ein real beobachteter Qualification-Runtime-PASS lag weiterhin nicht vor.

## Gewählter Schritt
Der kleinste sichere P0-Schritt ist die Konsistenzreparatur vor jeder weiteren Schreibfreigabe:

1. `RULE-013` kanonisch nachtragen.
2. `DELTA-0014` ausschließlich append-only ergänzen.
3. `RULE-014` für deterministische Browser-Derivate aufnehmen.
4. `DELTA-0015` append-only ergänzen.
5. `src/seed.js` und `src/deltas.js` exakt aus den kanonischen JSON-Daten synchronisieren.
6. Einen Fail-Closed-Wächter plus Regressionstest und CI-Gate ergänzen.

## Risikoanalyse
Der Schritt verändert keine produktiven Nutzerinhalte und führt keinen Inbox-Commit aus. Die einzigen Wissensänderungen sind additive Regeln und additive Delta-Ereignisse. Bestehende Delta-Ereignisse bleiben unverändert. Der Rückweg besteht aus dem Git-Vorgängerstand; bei Derivatdrift bleibt die Qualitätsfreigabe blockiert.

## Neue Regel
`RULE-014`: Browser-Derivate müssen deterministisch aus kanonischen Wissensquellen ableitbar sein.

Einordnung:
- Typ: Regel
- Hauptkategorie: Daten & Integrität
- Nebenkategorien: Single Source of Truth, Tests, Tool UI
- Reifegrad: E2
- Priorität: P0
- Gültigkeitsbereich: Projekt
- Projektbezug: PROVOWARE Knowledge & Project Intelligence
- Automatisierbarkeit: Ja
- Status: bestätigt
- Historie: `DELTA-0015`

## Validierung
Statisch nachweisbar:
- `RULE-013` und `RULE-014` sind im kanonischen Masterbuch vorhanden.
- `DELTA-0014` und `DELTA-0015` wurden am Ende der Historie ergänzt.
- `scripts/verify_browser_derivatives.py` vergleicht kanonische Quellen und Browser-Derivate bytegenau.
- `tests/test_browser_derivatives.py` fordert einen vollständigen PASS des Derivat-Wächters.
- `.github/workflows/browser-derivative-sync.yml` führt Wächter und Regressionstest mit 5-Minuten-Timeout aus.

Nicht als PASS gewertet:
- lokale Python-Ausführung: BLOCKED durch fehlende DNS-Auflösung von github.com beim Versuch, die öffentliche Repository-Baseline zu klonen.
- GitHub-Actions-Runtime: UNKNOWN_NOT_OBSERVED, solange kein konkreter grüner Run ausgelesen wurde.
- Qualification-Receipt-Runtime: UNKNOWN_NOT_OBSERVED.
- Browser-E2E: NOT_RUN.

## Datenverlustschutz und Rückfallfähigkeit
- keine Löschung bestehender Wissenseinträge
- keine Mutation bestehender Delta-Ereignisse
- keine produktive Wissensübernahme
- Git-Historie bleibt vollständiger Rückweg
- Derivatdrift ist fail-closed und blockiert die Qualitätsfreigabe

## Nächster Schritt
Iteration 015 — Commit-bound Qualification Evidence: den realen Qualification-Receipt-Lauf an den konkreten `source_commit_sha` binden und nur bei tatsächlich beobachtetem PASS die Einzelcommit-Qualifikation von E2 auf E3 anheben. Parallel den Derivat-Wächter auf `data/inbox.json → src/inbox.js` erweitern, falls die aktuelle Generatorform dort ebenfalls eindeutig reproduzierbar ist.
