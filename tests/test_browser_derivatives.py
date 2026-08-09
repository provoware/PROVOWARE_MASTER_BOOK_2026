#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_browser_derivatives as guard


def test_browser_derivatives_match_canonical_sources():
    result = guard.verify()
    assert result["result"] == "PASS", result
    assert all(result["checks"].values()), result


def test_expected_rendering_is_strict():
    assert guard.expected_seed().startswith("window.MASTERBOOK_SEED=")
    assert guard.expected_seed().endswith(";\n")
    assert guard.expected_deltas().startswith("window.KNOWLEDGE_DELTAS = ")
    assert guard.expected_deltas().endswith(";\n")
    assert guard.expected_seed() + "drift" != guard.SEED_TARGET.read_text(encoding="utf-8")


if __name__ == "__main__":
    test_browser_derivatives_match_canonical_sources()
    test_expected_rendering_is_strict()
    print("PASS: Browser-Derivate entsprechen den kanonischen Quellen")
