# PROVOWARE Codex-Kurzanweisung

Arbeite nur innerhalb des freigegebenen Iterationsplans und Scopes.

- Der aktuelle Plan ist nach Start eingefroren.
- Neue Anforderungen, Findings oder Verbesserungen gehen standardmäßig in die nächste Iteration.
- Unterbrich nur bei nachgewiesenem Konflikt mit Sicherheit, Ausgangs-SHA, Scope, Invariants oder Planvoraussetzungen.
- Vor produktiver Mutation HEAD, Recovery-/Iterationszustand und erlaubten/verbotenen Scope prüfen.
- Pro produktivem Scope darf nur ein autorisierter Executor schreiben.
- Tests dürfen in einem isolierten Evidence Lab echte Dateien und Fehlerzustände erzeugen; Produktivdaten bleiben getrennt.
- Kein PASS ohne tatsächlich ausgeführten Test; Gate-Evidence muss zum geprüften HEAD gehören.
- Keine stillen Refactorings, keine eigenständige Scope-Erweiterung und keine Nebenanforderungen heimlich umsetzen.
- Nach jeder Iteration Ergebnis, Evidence, Findings, nächsten erlaubten Schritt und Recovery-Zustand so dokumentieren, dass ein neuer Agent ohne alten Chat sicher fortfahren kann.
- Bei Unsicherheit nicht raten: Zustand prüfen, Finding erzeugen und kontrolliert weiterplanen.

Vollständige Grundlage: PROGRAMMIERDISZIPLIN_MANIFEST.md
