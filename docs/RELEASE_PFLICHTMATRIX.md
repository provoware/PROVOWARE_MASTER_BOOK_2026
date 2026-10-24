# Release-Pflichtmatrix – PROVOWARE Knowledge & Project Intelligence

Stand: 2026-10-24. Grundlage: GitHub-`main` bei Beginn `3b520b4a125e568869d4c6e63d2c7a2e8ff9b329`.
Arbeitszweig: `dev/browser-preflight-parity-20261024`; PR #29 (Entwurf). Geprüfter Funktions-HEAD: `7f50f1ea2cb85e095711196c866379a0a286ca29`. **Keine Gesamtfreigabe.**
`PASS` gilt ausschließlich für konkret nachgewiesene Prüfungen; `OPEN` bedeutet fehlenden vollständigen Nachweis, `BLOCKED` fehlende Release-Voraussetzung. Keine Prozentangaben.

| Pflichtbereich | Soll / Abnahmekriterium | Ist / Beleg | Status |
|---|---|---|---|
| Fachfunktionen | Lesen, Finden, Inbox, Verlauf, Vorschau vollständig | `index.html`, `preview.html`, `src/app.js`, `src/preview.js`; vollständige E2E-Prüfung fehlt | OPEN |
| Grenzfälle | Leere/defekte Eingaben, doppelte Quellen, Konflikte | Gemeinsame Browser-Vorprüfung `src/preflight.js`, Negativtests `tests/test_browser_preflight.cjs` | OPEN – Arbeitspaket-CI PASS; Gesamtprüfung offen |
| Datensicherheit | Kein stilles Schreiben, gesicherte Transaktionen | Vorschau bleibt nur lesend; produktive Schreibfreigabe gesperrt | BLOCKED |
| Wiederherstellung | Reproduzierbarer Abbruch/Undo, beschädigte Daten | `scripts/recovery_replay.py`, Tests vorhanden; Gesamtintegration fehlt | OPEN |
| Fehlerbehandlung | Fehler sichtbar, ungültige Kategorien/Beziehungen abgewiesen | Browser-Vorprüfung prüft kanonische Register; Browser-E2E offen | OPEN |
| Sicherheit | XSS, Pfad-/Eingabegrenzen, Rechte, Schutzregeln | HTML-Escaping in beiden Ansichten; umfassender Sicherheitstest offen | OPEN |
| Design und Lesbarkeit | Große Schrift, klare Rückmeldungen, Kontrast | CSS vorhanden; reale Sichtprüfung fehlt | OPEN |
| 800×600 + hohe Skalierung | Ohne horizontales Scrollen bedienbar | Chromium-Offline-Test auf `f5f8c0b` für 1280/800/400/320 und 200 % Schrift: [CI #40095636573](https://github.com/provoware/PROVOWARE_MASTER_BOOK_2026/actions/runs/40095636573) PASS; echter Browserzoom/Firefox offen | OPEN – Teilprüfung PASS |
| Tastatur und Barrierefreiheit | Fokus, Tastatur, Screenreader, Statusansagen | Echte Chromium-Tastaturauswahl in beiden Ansichten [PASS auf f5f8c0b](https://github.com/provoware/PROVOWARE_MASTER_BOOK_2026/actions/runs/40095636573); Screenreader/gesamte Navigation offen | OPEN – Teilprüfung PASS |
| Performance | Reaktionszeit, Speicher, große Datenmengen | Keine belastbaren Grenzwertmessungen | OPEN |
| Wartbarkeit | Gemeinsame Logik, kanonische Datenquellen | Gemeinsame Browser-Vorprüfung; Register aus JSON generiert | OPEN – Arbeitspaket-CI PASS; Gesamtprüfung offen |
| Paketierung und Installation | Offline-Start, reproduzierbares Paket | HTML-Offlinestart dokumentiert, Paket- und Frischinstallationstest offen | OPEN |
| Automatische Funktionstests | Positiv/Negativ und Fehlerfälle | Python-Tests vorhanden; neuer Node-Regressionstest und GitHub-Workflow | OPEN – Arbeitspaket-CI PASS; Gesamtprüfung offen |
| Integration | Browser/Python konsistent, Generatoren aktuell | Gemeinsame Browser-Vorprüfung, Derivat-Wächter erweitert | OPEN – Arbeitspaket-CI PASS; Gesamtprüfung offen |
| GUI/Browser | Chrome, Firefox, 800×600, Zoom, Tastatur | Chromium-Offline-Layout und Auswahl [PASS auf f5f8c0b](https://github.com/provoware/PROVOWARE_MASTER_BOOK_2026/actions/runs/40095636573); Firefox und echter Browserzoom offen | OPEN – Teilprüfung PASS |
| Regression und CI | Pflichtprüfungen grün auf identischem Commit | Sieben GitHub-Prüfjobs auf Funktions-HEAD `7f50f1e` erfolgreich; Gesamtrelease weiterhin ungeprüft | OPEN |
| Dokumentation | Aktuelle Start-, Test-, Wiederherstellungsanleitung | README überarbeitet; Fach-/Release-Dokumentation noch nicht vollständig | OPEN |
| Release-Vorbereitung | Stabiler, eingefrorener Kandidat mit Nachweisen | Nicht erreicht; keine Veröffentlichung | BLOCKED |

## Arbeitspaket dieses Entwicklungszweigs

**Fehlerbefund:** Python-`preflight.py` erkennt gleiche Quellenbehauptungen bei unterschiedlichem Titel als Dublette. Die Browser-Ansichten verwendeten abweichende, unvollständige Prüfungen; insbesondere `src/preview.js` konnte einen Kandidaten als READY anzeigen, den Python blockiert. Zusätzlich fehlten im Browser die kanonischen Kategorie- und Beziehungstypprüfungen.

**Umsetzung:** Ein gemeinsamer, ausschließlich lesender Browser-Preflight mit Pflichtfeldern, Kategorien, Beziehungstypen, E5-Schutz, Quellen-Tripel-Dubletten und Konflikten. Beide Ansichten verwenden dieselbe Funktion. Die Browser-Register stammen deterministisch aus `data/categories.json` und `data/relationship-types.json`; Derivat-Wächter und Negativtests schützen vor Drift.

**Sicherheitsinvarianten:** Keine Mutation von `data/masterbook_seed.json`, `data/inbox.json` oder `data/knowledge-deltas.json`; keine schreibende Übernahme; kein Merge und kein Release ohne grüne vorgeschriebene Prüfungen.

## Prüfbelege / nächster Schritt

- Vor dem GitHub-Schreiben: gemeinsame Browser-Vorprüfung mit realem Seed und Inbox im isolierten JavaScript-Kontext geprüft: INBOX-001 READY, INBOX-002 DUPLICATE, INBOX-003 CONFLICT, INBOX-004 BLOCKED. **Nur Vorabprüfung, kein CI-PASS.**
- GitHub-CI auf Funktions-HEAD `7f50f1ea2cb85e095711196c866379a0a286ca29`: **7/7 PASS** (Intent Guard, Browser Derivative Sync, Browser Preflight, Single Commit Qualification, Preview Evidence, Qualification Receipt Gate, RULE-015-Transaktion). Der ursprüngliche RULE-015-Gate-Fehler wurde reproduziert und durch Prüfung bereits aufgenommener Regeln samt Dubletten-Wiederholungsblockade repariert.
- Prüfbelege: [Browser Preflight](https://github.com/provoware/PROVOWARE_MASTER_BOOK_2026/actions/runs/40052166960), [Derivate](https://github.com/provoware/PROVOWARE_MASTER_BOOK_2026/actions/runs/40052166955), [RULE-015](https://github.com/provoware/PROVOWARE_MASTER_BOOK_2026/actions/runs/40052166989), [weitere Prüfungen im PR #29](https://github.com/provoware/PROVOWARE_MASTER_BOOK_2026/pull/29/checks).
- Nächster Schritt: finale CI nach diesem reinen Nachweis-Commit erneut prüfen; danach reale Browser- und Skalierungstests ergänzen. Nutzer-Endabnahme erst unmittelbar vor Veröffentlichung des vollständigen Release-Kandidaten.

## Folgepaket: Responsive Offline-Browser (2026-10-24)

- Ausgangspunkt: PR #29, HEAD `c62223646239fe9169b76997f67939061fe08e6a`; eigener Folgeentwicklungszweig `dev/responsive-browser-800-zoom-20261024`, keine Änderung an kanonischen Wissensdaten.
- Befund: `preview.html` überschrieb das responsive CSS-Raster durch ein Inline-Raster; lange Titel und Hashes konnten horizontales Scrollen verursachen.
- Änderung: Gemeinsame responsive Layoutregel, Umbruch langer Zeichenketten, größere Bedienelemente und sichtbarer Tastaturfokus. Echte Chromium-Regression für beide Offline-Ansichten bei 1280×720, 800×600, 400×300 und 320×568 sowie 200 % Schriftgröße und Tastaturauswahl.
- 400×300 ist eine enge CSS-Ansichtsgröße, **kein** Nachweis eines echten 200-%-Browserzooms. Echte Zoom-, Firefox- und Kubuntu-Sichtprüfungen bleiben offen.
- Prüfbeleg: **PASS** für die drei Chromium-Testmethoden und beide Ausführungen auf Funktions-HEAD `f5f8c0b99ad7afe1d02ae688bd4e994be236f733`: [Push-CI #40095621000](https://github.com/provoware/PROVOWARE_MASTER_BOOK_2026/actions/runs/40095621000), [PR-CI #40095636573](https://github.com/provoware/PROVOWARE_MASTER_BOOK_2026/actions/runs/40095636573). Dies ist keine Freigabe der Gesamtmatrix.
- Nächster Schritt: Browser-Gate auswerten, Fehler reparieren, anschließend weitere Tastatur-/Screenreader- und Browserprüfungen.
