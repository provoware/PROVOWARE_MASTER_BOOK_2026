from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json

from acceptance_preview import build_preview
from canonical_json import sha256_json

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify(candidate_id: str) -> dict:
    inbox = _load(ROOT / "data" / "inbox.json")["items"]
    seed = _load(ROOT / "data" / "masterbook_seed.json")
    candidate = next((item for item in inbox if item["candidate_id"] == candidate_id), None)
    if candidate is None:
        return {
            "schema_version": "1.0",
            "candidate_id": candidate_id,
            "run_a_hash": "sha256:" + "0" * 64,
            "run_b_hash": "sha256:" + "0" * 64,
            "plan_hash_a": "sha256:" + "0" * 64,
            "plan_hash_b": "sha256:" + "0" * 64,
            "equal": False,
            "result": "BLOCKED",
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "details": {"reason": "Kandidat nicht gefunden"},
        }

    run_a = build_preview(candidate, seed, plan_number=1)
    run_b = build_preview(candidate, seed, plan_number=1)
    run_a_hash = sha256_json(run_a)
    run_b_hash = sha256_json(run_b)
    plan_hash_a = run_a.get("after_hash") or sha256_json(run_a)
    plan_hash_b = run_b.get("after_hash") or sha256_json(run_b)
    equal = run_a == run_b and run_a_hash == run_b_hash and plan_hash_a == plan_hash_b
    result = "PASS" if equal and run_a.get("result") == "PREVIEW_READY" else "FAIL"
    return {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "run_a_hash": run_a_hash,
        "run_b_hash": run_b_hash,
        "plan_hash_a": plan_hash_a,
        "plan_hash_b": plan_hash_b,
        "equal": equal,
        "result": result,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "details": {
            "preview_result": run_a.get("result"),
            "target_entry_id": (run_a.get("after") or {}).get("id"),
            "plan_id": run_a.get("plan_id"),
            "undo_id": (run_a.get("undo_preview") or {}).get("undo_id"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prüft zwei unabhängige Preview-Läufe auf identische Ausgabe.")
    parser.add_argument("candidate_id", nargs="?", default="INBOX-001")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    evidence = verify(args.candidate_id)
    payload = json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if evidence["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
