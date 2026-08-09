#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
errors = []

def fail(message):
    errors.append(message)

payload = json.loads((ROOT / "data" / "knowledge-deltas.json").read_text(encoding="utf-8"))
items = payload.get("items", [])
ids = [item.get("event_id") for item in items]

if len(ids) != len(set(ids)):
    fail("Doppelte Delta-Event-IDs")

allowed = {"neu", "verbessert", "zusammengefuehrt", "konflikt", "reife_geaendert", "prioritaet_geaendert", "projektbezug_geaendert", "archiviert"}
status_allowed = {"historisch_rekonstruiert", "direkt_nachgewiesen"}
required = {"event_id", "schema_version", "timestamp", "iteration", "entry_id", "change_type", "reason", "source", "status"}

for item in items:
    missing = required - set(item)
    if missing:
        fail(f"{item.get('event_id')}: Pflichtfelder fehlen: {sorted(missing)}")
    if item.get("change_type") not in allowed:
        fail(f"{item.get('event_id')}: unbekannter change_type")
    if item.get("status") not in status_allowed:
        fail(f"{item.get('event_id')}: unbekannter Nachweisstatus")
    source = item.get("source") or {}
    if not source.get("ref") or not source.get("claim"):
        fail(f"{item.get('event_id')}: Quelle unvollständig")
    if item.get("status") == "direkt_nachgewiesen" and not item.get("after_hash"):
        fail(f"{item.get('event_id')}: direkt nachgewiesen ohne after_hash")

html = (ROOT / "index.html").read_text(encoding="utf-8")
if "src/deltas.js" not in html:
    fail("index.html lädt src/deltas.js nicht")
if 'data-view="history"' not in html:
    fail("History-Navigation fehlt")

if errors:
    print("FAIL")
    for error in errors:
        print("-", error)
    raise SystemExit(1)

print(f"PASS: {len(items)} Delta-Ereignisse, IDs/Typen/Quellen/History-Vertrag geprüft.")
