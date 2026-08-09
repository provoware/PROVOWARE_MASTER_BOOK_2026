# Iteration 011 — Single-Commit Qualification Chain

Ziel ist ein isolierter End-to-End-Nachweis für genau einen READY-Kandidaten: Preview Evidence → Commit Intent → Recovery Startup Gate → Transaction → Restart Replay → Commit Evidence.

Die Qualifikation darf nur PASS melden, wenn alle Teilstufen real ausgeführt und miteinander gebunden wurden. UNKNOWN, BLOCKED oder fehlende Evidence sind kein PASS.

Die Ausführung erfolgt ausschließlich in einer temporären Fixture-Kopie; kanonische Projektdaten dürfen durch die Qualifikation nicht verändert werden.
