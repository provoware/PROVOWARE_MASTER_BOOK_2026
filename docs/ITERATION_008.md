# Iteration 008 – Crash-konsistente Einzeltransaktion

## Ziel

Erstmals einen schreibenden Wissenspfad für genau einen `READY`-Kandidaten implementieren. Der Pfad bleibt an den bestehenden Preview-/Evidence-/Intent-Vertrag gebunden und darf bei Teilfehlern keinen inkonsistenten kanonischen Zustand hinterlassen.

## Ablauf

`COMMIT_READY → PREPARED → WRITING → VALIDATING → COMMITTED`

Fehlerpfad:

`Fehler → Rollback aus Backups → ROLLED_BACK`

Wenn selbst der Rollback scheitert:

`RECOVERY_REQUIRED`

## Betroffene kanonische Dateien

- `data/masterbook_seed.json`
- `data/knowledge-deltas.json`
- `data/inbox.json`

## Sicherheitsmechanismen

1. Nur `COMMIT_READY` darf den Schreibpfad betreten.
2. Zielzustand muss weiterhin mit Preview und Intent übereinstimmen.
3. Vor jeder Änderung werden Backups aller drei kanonischen Dateien erzeugt.
4. Zielstände werden zunächst in separate Temp-Dateien geschrieben und `fsync`-gesichert.
5. Ein Journal wird vor dem ersten Replace auf `PREPARED` persistiert.
6. Dateien werden mit `os.replace` ersetzt und der Verzeichniszustand wird synchronisiert.
7. Nach allen Replaces werden die geschriebenen JSON-Dokumente zurückgelesen und gegen die erwarteten SHA-256-Werte geprüft.
8. Erst dann wird `COMMITTED` gesetzt.
9. Jeder definierte Fehlerpfad versucht einen vollständigen Rollback aus den Vorher-Backups.
10. Rollbackfehler werden nicht verdeckt, sondern als `RECOVERY_REQUIRED` protokolliert.

## Fault-Injection-Matrix

Der Regressionstest deckt mindestens ab:

- `after_prepare`
- `before_replace_1`
- `after_replace_1`
- `before_replace_2`
- `after_replace_2`
- `before_replace_3`
- `after_replace_3`
- `before_validation`
- Non-READY-Kandidat bleibt `BLOCKED`

## Validierungsstatus

- Repository-Implementierung und Rücklesen: PASS
- Schema/Workflow statisch vorhanden: PASS_STATIC
- GitHub-Actions-Gate konfiguriert: CONFIGURED
- Runtime-Ausführung des Fault-Matrix-Tests in dieser Agentenlaufzeit: BLOCKED durch transienten Toolfehler
- Daher kein behauptetes Runtime-PASS

## Erkenntnis

`RULE-008`: Ein Wissens-Commit muss crash-konsistent journalisiert und rückrollbar sein. Reife bleibt E2, bis der reale Fault-Injection-Lauf grün nachgewiesen ist.

## Nächster Schritt

Iteration 009 – Recovery Replay + Commit-Evidence: vorhandene Journale beim Start deterministisch klassifizieren, `COMMITTED`/`ROLLED_BACK`/`RECOVERY_REQUIRED` rekonstruieren und für einen erfolgreichen Commit einen unveränderlichen Evidence-Datensatz erzeugen.
