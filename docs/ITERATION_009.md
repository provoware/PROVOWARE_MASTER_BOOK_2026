# Iteration 009 – Recovery Replay + Commit-Evidence

Stand: 2026-08-09

## Ziel

Nach einem Neustart oder Prozessabbruch müssen vorhandene Transaktionsjournale deterministisch bewertet werden. Ein erfolgreicher oder vollständig zurückgerollter Zustand darf nur dann als verifiziert gelten, wenn die aktuell beobachteten kanonischen Dateien zu den im Journal gespeicherten SHA-256-Werten passen.

## Neue Bausteine

- `schemas/commit-evidence.schema.json`
- `scripts/recovery_replay.py`
- `tests/test_recovery_replay.py`
- `.github/workflows/recovery-replay.yml`

## Recovery-Klassifikationen

- `CLEAN` – kein Journal vorhanden
- `COMMITTED_VERIFIED` – alle beobachteten Dateien entsprechen den erwarteten Nachher-Hashes
- `ROLLED_BACK_VERIFIED` – alle beobachteten Dateien entsprechen den Vorher-Hashes
- `RECOVERY_REQUIRED` – gemischter oder sonst nicht eindeutig sicherer Zustand
- `CORRUPT_JOURNAL` – Journal ist nicht lesbar oder strukturell unvollständig
- `HASH_MISMATCH` – behaupteter Endzustand stimmt nicht mit den Dateihashes überein

## Reparaturmodus

Der Standardlauf bleibt lesend. Mit `--repair` darf ein nicht eindeutiger Mischzustand ausschließlich aus den bereits vor der Transaktion erzeugten Backups auf den Vorher-Zustand zurückgesetzt werden. Danach werden die Vorher-Hashes erneut geprüft.

Ein fehlendes Backup oder eine fehlgeschlagene Wiederherstellung bleibt `RECOVERY_REQUIRED`.

## Commit-Evidence

Nur `COMMITTED_VERIFIED` und `ROLLED_BACK_VERIFIED` dürfen Evidence erzeugen.

Der Evidence-Datensatz enthält mindestens:

- Transaktions-ID
- Kandidaten-ID
- Intent-ID
- beobachteten Journalzustand
- Journal-Hash
- Vorher-Gesamtzustands-Hash
- Nachher-Gesamtzustands-Hash
- pro Zieldatei Vorher-, Nachher- und beobachteten Hash
- Evidence-Hash

Evidence wird unter `evidence/transactions/<TX-ID>.json` mit exklusiver Dateierstellung angelegt. Ein bereits existierender Nachweis wird nicht überschrieben.

## Sicherheitsinvarianten

1. Ein beschädigtes Journal kann niemals PASS erzeugen.
2. Ein Hash-Mismatch kann niemals PASS erzeugen.
3. Ein gemischter Zustand wird ohne expliziten Reparaturmodus nicht verändert.
4. Reparatur verwendet ausschließlich vorhandene Vorher-Backups.
5. Evidence wird nur für hashverifizierte Endzustände erzeugt.
6. Bestehende Evidence wird nicht still überschrieben.
7. `UNKNOWN`, `BLOCKED` und nicht ausgeführte Laufzeittests bleiben von PASS getrennt.

## Testmatrix

`tests/test_recovery_replay.py` deckt ab:

- Clean-Start ohne Journale
- verifizierter COMMITTED-Zustand
- unveränderliches, wiederholtes Evidence-Lesen
- verifizierter ROLLED_BACK-Zustand
- gemischter unvollständiger Zustand
- Wiederherstellung dieses Mischzustands aus Backups
- beschädigtes Journal blockiert den Lauf

## Bewusste Grenze

Iteration 009 schaltet noch keine automatische Massenübernahme frei. Der Recovery-Replay ist die Sicherheitsvoraussetzung für die spätere produktive Einzelübernahme und danach erst für Batch-Verarbeitung.

## Nächster technischer Schritt

Iteration 010 – Recovery Startup Gate + Single-Commit Qualification: Recovery-Replay beim Start als Pflichtgate auswerten, `COMMIT_READY` bei offenen Recovery-Fällen sperren und den ersten vollständigen Einzelpfad Preview → Intent → Commit → Restart-Replay → Evidence als zusammenhängende Qualifikation prüfen.
