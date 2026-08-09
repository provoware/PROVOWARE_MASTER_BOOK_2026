from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data' / 'inbox.json'
TARGET = ROOT / 'src' / 'inbox.js'


def main() -> int:
    payload = json.loads(SOURCE.read_text(encoding='utf-8'))
    rendered = 'window.KNOWLEDGE_INBOX = ' + json.dumps(payload, ensure_ascii=False, indent=2) + ';\n'
    TARGET.write_text(rendered, encoding='utf-8')
    print(f'Erzeugt: {TARGET.relative_to(ROOT)} aus {SOURCE.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
