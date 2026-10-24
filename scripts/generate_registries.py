#!/usr/bin/env python3
"""Reproduzierbare Browser-Registries aus kanonischen JSON-Quellen."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def render() -> str:
    categories = json.loads((ROOT / "data/categories.json").read_text(encoding="utf-8"))["categories"]
    relations = json.loads((ROOT / "data/relationship-types.json").read_text(encoding="utf-8"))["relationship_types"]
    compact = lambda data: json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return (
        "window.MASTERBOOK_CATEGORIES=" + compact(categories) + ";\n"
        "window.MASTERBOOK_RELATIONSHIP_TYPES=" + compact(relations) + ";\n"
    )


if __name__ == "__main__":
    target = ROOT / "src/registries.js"
    target.write_text(render(), encoding="utf-8")
    print("OK: src/registries.js aus kanonischen Registern erzeugt")
