# Iteration 010 – Recovery Startup Gate

## Ziel

Vor **jedem** neuen Wissensschreibvorgang wird zentral geprüft, ob ältere Recovery-Journale einen eindeutig sicheren Zustand besitzen. Neue Mutationen bleiben gesperrt, solange `RECOVERY_REQUIRED`, `HASH_MISMATCH` oder `CORRUPT_JOURNAL` existiert.

## Gewählter Minimal-Schritt

Iteration 010 trennt bewusst das globale Startup-Gate von der vollständigen Single-Commit-Qualifikation. Grund: Das Gate muss zuerst selbst schreibfrei, deterministisch und nicht umgehbar sein. Die End-to-End-Qualifikation folgt erst danach.

## Ablauf

```text
Programm/Schreibpfad
        ↓
Recovery Startup Gate
        ↓
alle TX-Journale nur klassifizieren
        ↓
RECOVERY_REQUIRED / HASH_MISMATCH / CORRUPT_JOURNAL?
        ├─ ja  → WRITE_BLOCKED
        └─ nein → WRITE_ALLOWED
                     ↓
                Intent prüfen
                     ↓
                Transaktion
```

## Sicherheitsentscheidung

Das Startup-Gate ruft **nicht** `replay_all()` auf. `replay_all()` kann für verifizierte Endzustände Commit-Evidence erzeugen. Eine Startup-Prüfung soll dagegen rein lesend bleiben. Daher verwendet `recovery_startup_gate.py` ausschließlich `classify_journal()`.

## Geänderte Komponenten

- `schemas/write-gate.schema.json`
- `scripts/recovery_startup_gate.py`
- `scripts/knowledge_transaction.py`
- `tests/test_recovery_startup_gate.py`
- `.github/workflows/recovery-startup-gate.yml`
- Masterbuch: `RULE-010`
- Delta-Ledger: `DELTA-0011`

## Gate-Regeln

`WRITE_ALLOWED` nur wenn:

- kein Recovery-Journal existiert, oder
- jedes vorhandene Journal als `COMMITTED_VERIFIED` oder `ROLLED_BACK_VERIFIED` klassifiziert wird.

`WRITE_BLOCKED` wenn mindestens eines gilt:

- `RECOVERY_REQUIRED`
- `HASH_MISMATCH`
- `CORRUPT_JOURNAL`

Unbekannte oder beschädigte Zustände werden niemals positiv interpretiert.

## Datenverlustschutz

Das Gate selbst:

- verändert keine kanonische Wissensdatei,
- erzeugt keine Evidence,
- führt kein automatisches Repair aus,
- verändert kein Journal.

Der Transaktionspfad ruft das Gate als erste Schreibbezogene Schutzprüfung auf. Ein blockierender Recovery-Zustand verhindert damit den Eintritt in `build_target_documents()` und jede Backup-/Temp-/Replace-Phase.

## Rückfallfähigkeit

Die Iteration ist klein und reversibel: Entfernen der Gate-Integration aus `knowledge_transaction.py` und der neu hinzugefügten Gate-Dateien stellt den vorherigen Stand wieder her. Kanonische Nutzdaten werden durch diese Iteration nicht migriert.

## Laufzeitstatus

CI ist konfiguriert. Ein PASS darf erst nach real beobachtetem GitHub-Actions-Lauf gesetzt werden.

## Nächster Schritt

Iteration 011 – Single-Commit Qualification Chain: den vollständigen Pfad `Preview Evidence → Commit Intent → WRITE_GATE → Transaction → Restart-Replay → Commit Evidence` in einer isolierten Fixture ausführen und als zusammenhängenden Qualifikationsnachweis binden.
