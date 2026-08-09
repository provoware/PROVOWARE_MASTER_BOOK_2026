from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data' / 'masterbook_seed.json'
TARGET = ROOT / 'src' / 'seed.js'


def render() -> str:
    data = json.loads(SOURCE.read_text(encoding='utf-8'))
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    return f'window.MASTERBOOK_SEED={payload};\n'


def main() -> int:
    TARGET.write_text(render(), encoding='utf-8')
    print(f'OK: {TARGET.relative_to(ROOT)} aus {SOURCE.relative_to(ROOT)} erzeugt')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
