# Iteration 007 – Commit-Intent Contract + Stale-Plan Guard

## Ziel

Vor einem späteren echten Wissensschreibvorgang wird ein ausschließlich lesender Intent erzeugt. Dieser Intent ist an den unveränderten kanonischen Projektzustand, die reproduzierbare Preview-Evidence, den geplanten Zielhash, die Ziel-ID, den Undo-Plan und eine begrenzte Gültigkeitszeit gebunden.

## Ablauf

1. Preview-Evidence für genau einen Inbox-Kandidaten prüfen.
2. Kanonischen Projektzustand aus den relevanten JSON-Quelldateien hashen.
3. Zielzustand und Undo-Plan aus der bestehenden Preview ableiten.
4. Intent erzeugen, ohne kanonische Wissensdaten zu verändern.
5. Vor einer späteren Nutzung erneut Evidence, Projektzustand, Zielhash, Ziel-ID, Undo-Hash und Ablaufzeit prüfen.
6. Bei jeder Abweichung `STALE` oder `BLOCKED` statt Freigabe liefern.

## Kanonischer Projektzustand

Der `project_state_hash` bindet derzeit:

- `data/masterbook_seed.json`
- `data/categories.json`
- `data/relationship-types.json`
- `data/inbox.json`

Damit werden genau die Eingaben erfasst, die den aktuellen Wissens- und Preflight-Zustand bestimmen.

## Neue Artefakte

- `schemas/commit-intent.schema.json`
- `scripts/project_state.py`
- `scripts/intent_guard.py`
- `tests/test_intent_guard.py`
- `.github/workflows/intent-guard.yml`
- `RULE-007`
- `DELTA-0008`

## Sicherheitsgrenzen

- Kein echter Wissens-Commit in Iteration 007.
- Kein automatisches Entfernen oder Verschieben eines Inbox-Kandidaten.
- Kein `DUPLICATE`, `CONFLICT` oder `BLOCKED` wird zu `COMMIT_READY` hochgestuft.
- Ablaufzeit oder geänderter Projektzustand ergeben `STALE`.
- Nicht ausgeführte Laufzeittests werden nicht als PASS dokumentiert.

## Geplantes Gate

`tests/test_intent_guard.py` prüft mindestens:

- READY-Kandidat erzeugt einen gebundenen Intent.
- DUPLICATE bleibt BLOCKED.
- abgelaufener Intent wird STALE.
- veränderter Projektzustand wird STALE.
- veränderter Zielhash wird STALE.

## Nächster technischer Schritt

Iteration 008 darf erst nach grünem Intent-Guard-Gate einen ersten echten, atomaren Commitpfad für exakt einen READY-Kandidaten entwerfen. Dieser Pfad muss Vorher-Snapshot, transaktionales Schreiben, Rücklesen, Hashprüfung, Delta-Erzeugung und Recovery bei Teilfehlern enthalten.
