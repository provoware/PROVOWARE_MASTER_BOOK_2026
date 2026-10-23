# Sicherheitsnachtrag – 23.10.2026: Dublettenprüfung bei Wissenseingang

- **Ausgangsstand:** `aaf8bf227f0213762ad2f86fe55000fb6d760468` nach PR #27.
- **Konkreter Fehler:** Main-CI „Intent Guard“ #39984384331 und „Preview Evidence“ #39984384262 schlagen bei `INBOX-002` fehl. Die Vorschau ließ den Testkandidaten als READY durch, obwohl `RULE-002` denselben konkreten Quellenanspruch enthält. Nur exakte Titel wurden als Dubletten behandelt.
- **Änderung:** Bei gleichem Eintragstyp zusätzlich das exakte Paar aus Quellentyp, Referenz und Quellenbehauptung vergleichen; vollständiges Triple muss gleich sein. Bestehende Titelprüfung bleibt erhalten.
- **Regression:** Anders formulierter Titel mit identischer Quelle wird DUPLICATE; gleiche Referenz mit abweichender Behauptung bleibt READY. Vorhandener Acceptance-Preview-Test deckt `INBOX-002` ab.
- **Keine Datenmutation:** Nur Vorprüfung, Regressionstest und dieses Protokoll; keine Änderungen an Seed, Wissensinbox oder Persistenz.
- **Restrisiko:** Inhaltlich sinngleiche Kandidaten aus unterschiedlichen Quellen bleiben ggf. unerkannt. Für unsichere Fuzzy-Dubletten keine automatische Löschung oder Zusammenführung.
- **Gates:** `tests/test_preflight.py`, `tests/test_acceptance_preview.py` sowie Intent-/Preview- und Receipt-Workflows auf neuem SHA prüfen. Kein erneuter Merge vor vollständigem Grün.
