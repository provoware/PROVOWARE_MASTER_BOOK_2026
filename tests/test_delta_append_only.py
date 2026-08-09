#!/usr/bin/env python3
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_delta_append_only import verify_append_only


def event(event_id: str, reason: str) -> dict:
    return {"event_id": event_id, "reason": reason}


def ledger(items: list[dict]) -> dict:
    return {"schema_version": "1.0", "items": items}


def must_fail(old: dict, new: dict) -> None:
    try:
        verify_append_only(old, new)
    except ValueError:
        return
    raise AssertionError("Änderung hätte blockiert werden müssen")


def main() -> None:
    baseline = ledger([event("DELTA-0001", "A"), event("DELTA-0002", "B")])

    appended = copy.deepcopy(baseline)
    appended["items"].append(event("DELTA-0003", "C"))
    result = verify_append_only(baseline, appended)
    assert result["status"] == "PASS"
    assert result["appended_events"] == ["DELTA-0003"]

    mutated = copy.deepcopy(appended)
    mutated["items"][0]["reason"] = "VERÄNDERT"
    must_fail(baseline, mutated)

    deleted = ledger([event("DELTA-0002", "B")])
    must_fail(baseline, deleted)

    reordered = ledger([event("DELTA-0002", "B"), event("DELTA-0001", "A")])
    must_fail(baseline, reordered)

    duplicate = ledger([event("DELTA-0001", "A"), event("DELTA-0001", "A")])
    must_fail(baseline, duplicate)

    print("PASS: Delta-Append-only-Regressionsmatrix")


if __name__ == "__main__":
    main()
