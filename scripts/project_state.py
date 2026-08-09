from __future__ import annotations

from pathlib import Path
import json

from canonical_json import sha256_json

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_STATE_FILES = (
    "data/masterbook_seed.json",
    "data/categories.json",
    "data/relationship-types.json",
    "data/inbox.json",
)


def _load_json(relative_path: str):
    path = ROOT / relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def project_state_manifest() -> dict:
    files = []
    for relative_path in CANONICAL_STATE_FILES:
        payload = _load_json(relative_path)
        files.append({
            "path": relative_path,
            "content_hash": sha256_json(payload),
        })
    return {
        "schema_version": "1.0",
        "files": files,
    }


def project_state_hash() -> str:
    return sha256_json(project_state_manifest())


if __name__ == "__main__":
    print(project_state_hash())
