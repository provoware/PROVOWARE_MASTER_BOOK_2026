# Iteration 006 – Preview Evidence Contract + Reproducibility Gate

## Ziel

Vor einem späteren Commit-Intent muss nachweisbar sein, dass zwei unabhängige Preview-Läufe für denselben READY-Kandidaten denselben Zielzustand und dieselben Hashwerte erzeugen.

## Ablauf

1. Kandidat `INBOX-001` laden.
2. Preview A mit identischem Ausgangsbestand erzeugen.
3. Preview B unabhängig erneut erzeugen.
4. Gesamtausgabe beider Läufe kanonisch hashen.
5. Zielzustands-/Plan-Hashes vergleichen.
6. Nur bei vollständiger Gleichheit `PASS` erzeugen.
7. Evidence als JSON-Artefakt ausgeben.

## Sicherheitsregeln

- Ein unbekannter Kandidat ergibt `BLOCKED`.
- `PREVIEW_BLOCKED` darf niemals als Reproduzierbarkeits-PASS gelten.
- Fehlende oder abweichende Hashes ergeben `FAIL`.
- Es findet weiterhin kein kanonischer Wissensschreibvorgang statt.
- Keine automatische E5-Hochstufung.
- Keine automatische Dubletten- oder Konfliktauflösung.

## Artefakte

- `schemas/preview-evidence.schema.json`
- `scripts/verify_preview_reproducibility.py`
- `tests/test_preview_reproducibility.py`
- `.github/workflows/preview-evidence.yml`

## Validierung

Der Workflow führt ohne zusätzliche Python-Abhängigkeiten `tests/test_acceptance_preview.py` und anschließend den Reproduzierbarkeitsprüfer aus. Das Evidence-Artefakt wird nur dann als PASS akzeptiert, wenn `equal=true`, beide Run-Hashes identisch und beide Plan-Hashes identisch sind.

## Rückfall

Iteration 006 ist additiv. Sie verändert keine bestehenden Wissenseinträge semantisch außer der dokumentierten Aufnahme von `RULE-006` und `DELTA-0007`. Entfernen der neuen Gate-Dateien stellt Iteration 005 funktional wieder her.

## Nächster Schritt

Iteration 007 – Commit-Intent Contract für genau einen READY-Kandidaten, weiterhin ohne tatsächlichen Commit. Der Intent muss Preview-Evidence, erwarteten Ausgangsbestand, Zielhash, Undo-Plan und Ablaufdatum binden.
