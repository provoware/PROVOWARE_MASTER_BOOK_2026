#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

import apply_rule_intake as intake

TARGETS = (intake.SEED, intake.DELTAS, intake.SEED_JS, intake.DELTAS_JS)


def snapshot() -> dict[Path, bytes]:
    return {path: path.read_bytes() for path in TARGETS}


def restore(before: dict[Path, bytes]) -> None:
    errors: list[str] = []
    for path, payload in before.items():
        fd, tmp_name = tempfile.mkstemp(prefix=f'.{path.name}.rollback.', dir=path.parent)
        try:
            with os.fdopen(fd, 'wb') as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, path)
        except Exception as exc:
            errors.append(f'{path}: {exc}')
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
    if errors:
        raise RuntimeError('Rollback unvollstaendig: ' + '; '.join(errors))


def apply_with_rollback(state: dict, fail_after: int | None = None) -> None:
    before = snapshot()
    writes = [
        (intake.SEED, intake.compact(state['seed']) + '\n'),
        (intake.DELTAS, intake.compact(state['ledger']) + '\n'),
        (intake.SEED_JS, state['seed_js']),
        (intake.DELTAS_JS, state['deltas_js']),
    ]
    try:
        for index, (path, text) in enumerate(writes, start=1):
            intake.atomic_write(path, text)
            if fail_after == index:
                raise RuntimeError(f'FAULT_INJECTION_AFTER_{index}')
    except Exception:
        restore(before)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description='RULE-Aufnahme mit Vier-Artefakt-Rollback')
    parser.add_argument('--candidate', type=Path, default=intake.DEFAULT_CANDIDATE)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--fail-after', type=int, choices=(1, 2, 3, 4), help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        state = intake.planned_state(args.candidate)
        if args.apply:
            apply_with_rollback(state, args.fail_after)
            state['receipt']['status'] = 'APPLIED_WITH_ROLLBACK_GUARD'
        print(json.dumps(state['receipt'], ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
