# Release-Pflichtmatrix – PROVOWARE Knowledge & Project Intelligence

Stand: 2026-10-24. Grundlage: GitHub-`main` bei Beginn `3b520b4a125e568869d4c6e63d2c7a2e8ff9b329`.
Arbeitszweig: `dev/browser-preflight-parity-20261024`. **Keine Gesamtfreigabe.**
`PASS` gilt ausschließlich für konkret nachgewiesene Prüfungen; `OPEN` bedeutet fehlenden vollständigen Nachweis, `BLOCKED` fehlende Release-Voraussetzung. Keine Prozentangaben.

| Pflichtbereich | Soll / Abnahmekriterium | Ist / Beleg | Status |
|---|---|---|---|
| Fachfunktionen | Lesen, Finden, Inbox, Verlauf, Vorschau vollständig | `index.html`, `preview.html`, `src/app.js`, `src/preview.js`; vollständige E2E-Prüfung fehlt | OPEN |
| Grenzfälle | Leere/defekte Eingaben, doppelte Quellen, Konflikte | Gemeinsame Browser-Vorprüfung `src/preflight.js`, Negativtests `tests/test_browser_preflight.cjs` | OPEN – CI prüfen |
| Datensicherheit | Kein stilles Schreiben, gesicherte Transaktionen | Vorschau bleibt nur lesend; produktive Schreibfreigabe gesperrt | BLOCKED |
| Wiederherstellung | Reproduzierbarer Abbruch/Undo, beschädigte Daten | `scripts/recovery_replay.py`, Tests vorhanden; Gesamtintegration fehlt | OPEN |
| Fehlerbehandlung | Fehler sichtbar, ungültige Kategorien/Beziehungen abgewiesen | Browser-Vorprüfung prüft kanonische Register; Browser-E2E offen | OPEN |
| Sicherheit | XSS, Pfad-/Eingabegrenzen, Rechte, Schutzregeln | HTML-Escaping in beiden Ansichten; umfassender Sicherheitstest offen | OPEN |
| Design und Lesbarkeit | Große Schrift, klare Rückmeldungen, Kontrast | CSS vorhanden; reale Sichtprüfung fehlt | OPEN |
| 800×600 + hohe Skalierung | Ohne horizontales Scrollen bedienbar | Reale Browserprüfung fehlt; `preview.html` nutzt noch starres Inline-Raster | OPEN |
| Tastatur und Barrierefreiheit | Fokus, Tastatur, Screenreader, Statusansagen | Karten mit Enter/Leertaste; vollständige Prüfung fehlt | OPEN |
| Performance | Reaktionszeit, Speicher, große Datenmengen | Keine belastbaren Grenzwertmessungen | OPEN |
| Wartbarkeit | Gemeinsame Logik, kanonische Datenquellen | Gemeinsame Browser-Vorprüfung; Register aus JSON generiert | OPEN – CI prüfen |
| Paketierung und Installation | Offline-Start, reproduzierbares Paket | HTML-Offlinestart dokumentiert, Paket- und Frischinstallationstest offen | OPEN |
| Automatische Funktionstests | Positiv/Negativ und Fehlerfälle | Python-Tests vorhanden; neuer Node-Regressionstest und GitHub-Workflow | OPEN – CI prüfen |
| Integration | Browser/Python konsistent, Generatoren aktuell | Gemeinsame Browser-Vorprüfung, Derivat-Wächter erweitert | OPEN – CI prüfen |
| GUI/Browser | Chrome, Firefox, 800×600, Zoom, Tastatur | Kein vollständiger realer E2E-Beleg | OPEN |
| Regression und CI | Pflichtprüfungen grün auf identischem Commit | Main-Workflows vor Änderung beobachtet; PR-HEAD noch nicht geprüft | OPEN |
| Dokumentation | Aktuelle Start-, Test-, Wiederherstellungsanleitung | README überarbeitet; Fach-/Release-Dokumentation noch nicht vollständig | OPEN |
| Release-Vorbereitung | Stabiler, eingefrorener Kandidat mit Nachweisen | Nicht erreicht; keine Veröffentlichung | BLOCKED |

## Arbeitspaket dieses Entwicklungszweigs

**Fehlerbefund:** Python-`preflight.py` erkennt gleiche Quellenbehauptungen bei unterschiedlichem Titel als Dublette. Die Browser-Ansichten verwendeten abweichende, unvollständige Prüfungen; insbesondere `src/preview.js` konnte einen Kandidaten als READY anzeigen, den Python blockiert. Zusätzlich fehlten im Browser die kanonischen Kategorie- und Beziehungstypprüfungen.

**Umsetzung:** Ein gemeinsamer, ausschließlich lesender Browser-Preflight mit Pflichtfeldern, Kategorien, Beziehungstypen, E5-Schutz, Quellen-Tripel-Dubletten und Konflikten. Beide Ansichten verwenden dieselbe Funktion. Die Browser-Register stammen deterministisch aus `data/categories.json` und `data/relationship-types.json`; Derivat-Wächter und Negativtests schützen vor Drift.

**Sicherheitsinvarianten:** Keine Mutation von `data/masterbook_seed.json`, `data/inbox.json` oder `data/knowledge-deltas.json`; keine schreibende Übernahme; kein Merge und kein Release ohne grüne vorgeschriebene Prüfungen.

## Prüfbelege / nächster Schritt

- Vor dem GitHub-Schreiben: gemeinsame Browser-Vorprüfung mit realem Seed und Inbox im isolierten JavaScript-Kontext geprüft: INBOX-001 READY, INBOX-002 DUPLICATE, INBOX-003 CONFLICT, INBOX-004 BLOCKED. **Nur Vorabprüfung, kein CI-PASS.**
- GitHub-CI und PR-HEAD: zunächst `PENDING`; konkrete Lauf-URLs nach Ausführung ergänzen.
- Nächster Schritt: GitHub-Prüfläufe auswerten und Fehler auf demselben Zweig beheben; danach reale Browser- und Skalierungstests ergänzen. Nutzer-Endabnahme erst unmittelbar vor Veröffentlichung des vollständigen Release-Kandidaten.
