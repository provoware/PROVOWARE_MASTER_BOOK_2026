#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SEED_SOURCE = ROOT / "data" / "masterbook_seed.json"
SEED_TARGET = ROOT / "src" / "seed.js"
DELTA_SOURCE = ROOT / "data" / "knowledge-deltas.json"
DELTA_TARGET = ROOT / "src" / "deltas.js"


def _compact_json(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def expected_seed() -> str:
    return f"window.MASTERBOOK_SEED={_compact_json(SEED_SOURCE)};\n"


def expected_deltas() -> str:
    return f"window.KNOWLEDGE_DELTAS = {_compact_json(DELTA_SOURCE)};\n"


def verify() -> dict:
    checks = {
        "seed_derivative_exact": SEED_TARGET.read_text(encoding="utf-8") == expected_seed(),
        "delta_derivative_exact": DELTA_TARGET.read_text(encoding="utf-8") == expected_deltas(),
    }
    return {
        "schema_version": "1.0",
        "result": "PASS" if all(checks.values()) else "BLOCKED",
        "checks": checks,
        "canonical_sources": [
            str(SEED_SOURCE.relative_to(ROOT)),
            str(DELTA_SOURCE.relative_to(ROOT)),
        ],
        "derived_targets": [
            str(SEED_TARGET.relative_to(ROOT)),
            str(DELTA_TARGET.relative_to(ROOT)),
        ],
    }


def main() -> int:
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["result"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
