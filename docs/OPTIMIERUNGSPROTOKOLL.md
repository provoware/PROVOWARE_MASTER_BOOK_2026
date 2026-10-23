# Optimierungsprotokoll – Qualification-Receipt
## 2026-10-23: unvollständige Prüfbelege blockieren

- **Basis:** `22cf6fc6fc026d1da37a769e7c8b3fe6913250a7` und lokal vorbereiteter Patch vom 21.10.2026.
- **Befund:** `all(receipt.get('checks', {}).values())` akzeptiert fälschlich leere `checks` und fehlende Teilprüfungen (`all([]) == True`). Auch `1` wurde wie echtes `True` behandelt. Der Hash kann bei manipulierten Belegen neu berechnet werden.
- **Änderung:** Die sechs vom Generator tatsächlich gelieferten Pflichtprüfungen sind ausdrücklich und streng mit `is True` erforderlich. Zusätzliche Checks müssen ebenfalls exakt `True` sein. Strukturfehler werden blockiert.
- **Regression:** Neu berechnete, formal passende Receipt-Hashes mit leeren, teilweisen, numerischen, fehlgeschlagenen oder falsch typisierten Prüfpunkten müssen trotzdem BLOCKED ergeben.
- **Scope:** Ausschließlich Gate-Logik, zugehörige Regressionstests und dieses Protokoll; keine echten Projekt-Transaktionen oder Datenmigrationen.
- **Vorheriger Testbeleg:** Isolierte Testkopie vom 21.10.2026: 5 Fallgruppen nach Patch PASS; keine Aussage über CI des neuen Commits.
- **Ausstehend:** Original-Repo-Tests und CI auf diesem Branch; Freigabe nur nach nachweislich grünen Gates.
- **Entwicklungszweig:** `sync/20261023-receipt-inner-checks` – Commits und PR siehe GitHub-Verlauf.
