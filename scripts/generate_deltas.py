#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "data" / "knowledge-deltas.json"
target = ROOT / "src" / "deltas.js"

payload = json.loads(source.read_text(encoding="utf-8"))
target.write_text(
    "window.KNOWLEDGE_DELTAS = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
    encoding="utf-8",
)
print(f"OK: {source.relative_to(ROOT)} -> {target.relative_to(ROOT)}")
