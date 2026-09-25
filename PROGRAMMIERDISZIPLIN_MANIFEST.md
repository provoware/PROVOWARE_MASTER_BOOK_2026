# PROVOWARE Programmierdisziplin-Manifest

## Zweck
Dieses Manifest definiert den globalen Entwicklungsstandard für alle PROVOWARE-Repositories, Menschen, Codex-Läufe, Subagenten und Automationen.

## Kernprinzip
Softwareentwicklung wird als kontrollierter Zustandsübergang behandelt. Jede Änderung braucht einen nachvollziehbaren Ursprung, einen freigegebenen Scope, reproduzierbare Evidence, einen bestätigten Abschlusszustand und einen sicheren Wiederanlaufpunkt.

## 1. Frozen Current Plan
Sobald eine Iteration freigegeben ist, bleibt ihr Plan unverändert. Neue Ideen, TODOs, Findings, CI-Hinweise oder Verbesserungen werden erfasst, aber standardmäßig für die nächste Iteration geplant.

Leitsatz: Neue Information erweitert die Zukunft und verändert nicht rückwirkend die Gegenwart.

## 2. Conflict Gate
Eine laufende Iteration darf nur gestoppt werden, wenn ein neuer Befund nachweislich eine Planvoraussetzung, Sicherheit, Ausgangs-SHA, erlaubten Scope, Invariant oder die Erreichbarkeit des erwarteten Ergebnisses verletzt.

## 3. Single Writer + Write Lease
Pro produktivem Scope darf gleichzeitig nur ein autorisierter Executor schreiben. Das Schreibrecht ist an Iteration, Scope und Ausgangs-SHA gebunden. Ändert sich die Grundlage, verfällt die Berechtigung.

## 4. Rollen
- Intake: erfasst und normalisiert neue Anforderungen.
- Checker: prüft Aussagen und arbeitet aktiv im Evidence Lab, aber nicht mutierend an Produktivdaten.
- Planner: erstellt Scope, Reihenfolge, Tests, Gates und Rückfallstrategie.
- Executor: führt ausschließlich den freigegebenen Plan im erlaubten Scope aus.
- Validator/Gatekeeper: prüft Diff, SHA, Scope, Evidence, Invariants und Regressionen unabhängig vom Executor.

## 5. Next-Iteration Queue
Neue Anforderungen werden append-only erfasst und können Beziehungen tragen: BLOCKS, REQUIRES, DEPENDS_ON, SUPERSEDES, DUPLICATE_OF, CONFLICTS_WITH, AFTER und RELATED_TO.

## 6. Evidenzstatus
Aussagen werden getrennt nach OBSERVED, SUSPECTED, REPRODUCED, CONFIRMED und DISPROVED. Eine plausible Vermutung ist kein bestätigter Befund.

## 7. Controlled Evidence Lab
Prüfer dürfen in isolierten temporären Testbereichen echte Dateien erzeugen, verändern, löschen und beschädigen; konkurrierende Writer, Prozessabbrüche, veraltete SHAs, Recovery, Timeouts und andere Fehlerzustände dürfen aktiv simuliert werden. Produktive Daten bleiben geschützt.

## 8. Evidence-Integrität
Kein PASS ohne tatsächlich ausgeführten Test. Evidence gilt nur für den geprüften Head. Codeänderung nach Test erfordert erneute relevante Prüfung.

## 9. Invariants und Negativtests
Projektweite Invariants gelten unabhängig von der aktuellen Iteration. Schutzmechanismen müssen auch durch absichtlich falsche Zustände getestet werden, etwa zweiter Writer, falscher SHA, Scope-Verstoß, ungültiger Recovery-Key und PASS ohne Evidence.

## 10. Recovery Key
Jeder bestätigte Zustand hinterlässt einen Wiederanlauf-Schlüssel mit mindestens: letzter bestätigter Head, Iteration, Ziel, Frozen Plan, abgeschlossene Schritte, offener Schritt, erlaubter/verbotener Scope, offene Findings, Next Queue, erforderliche Gates und nächster erlaubter Schritt.

Kein Agent muss sich erinnern. Kein Agent darf fehlenden Kontext erraten.

## 11. Traceability
Änderungen sollen rückverfolgbar sein:
Requirement/Decision → Finding → Plan → Change → Test/Evidence → Gate/Checkpoint.

## 12. Entscheidungsjournal
Wichtige menschliche Entscheidungen werden mit ID und Begründung dokumentiert, damit spätere Agenten sie nicht versehentlich wieder als offene Frage behandeln.

## 13. Scope und Budget
Jede Iteration erhält einen begrenzten Scope. Scope-Wachstum wird sichtbar gemacht und bei Bedarf in Folgeiterationen zerlegt. Geänderte, aber nicht geplante Bereiche müssen leer oder explizit begründet sein.

## 14. Risikobasierte Gates
Gate-Profile können Docs, Governance, Scope, Product, Database, UI, Accessibility, Browser, Network, Recovery und Deep umfassen. Prüfungstiefe richtet sich nach tatsächlichem Risiko und betroffenen Bereichen.

## 15. Idempotenz und Recovery
Wiederholbare Schritte werden bevorzugt. Ein Abbruch darf nie einen unklaren bestätigten Zustand hinterlassen.

## 16. Minimal Reproduction
Fehler sollen nach Möglichkeit auf einen kleinsten reproduzierbaren Fall reduziert werden, bevor umfangreiche Reparaturen geplant werden.

## 17. Rebuild-Test
Ein frischer Agent ohne Chatverlauf muss aus Repository, Git-Historie und Kontrollmetadaten bestimmen können, wo das Projekt steht, warum, was gesperrt ist, was erlaubt ist und was als Nächstes geschehen darf. Scheitert das, ist der Context-Key unvollständig.

## 18. Sichtbarer Fortschritt
Längere Prüfungen zeigen aktuellen Schritt, Gesamtfortschritt, aktiven Test, erwartetes Ergebnis, tatsächliches Ergebnis, Laufzeit und Ampelstatus. Die Anzeige visualisiert technische Evidence, ersetzt sie aber nicht.

## 19. Globale Vererbung
Hierarchie:
Global Development Contract → Project Profile → Iteration Contract.
Lokale Regeln dürfen globale Sicherheits- und Nachvollziehbarkeitsregeln verschärfen, aber nicht stillschweigend abschwächen.

## 20. Schlussregel
Der Entwicklungsprozess selbst ist Teil des Produkts. Er muss nicht nur funktionierenden Code erzeugen, sondern auch erklären können, warum eine Änderung existiert, wie sie geprüft wurde, wie Fehler erkannt werden und wie ein neuer Agent sicher fortsetzen kann.

## Leitsatz
**Kein Agent muss sich erinnern. Kein Agent darf raten. Keine Änderung verliert ihren Ursprung. Kein PASS existiert ohne Evidence. Keine neue Idee muss verloren gehen. Keine neue Idee darf ungeprüft den laufenden Plan verändern. Jeder bestätigte Zustand muss sicher wiederaufnehmbar sein.**
