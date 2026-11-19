"""Publish maintained static page sources to their existing public URLs."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(check=False, product_only=False, spanish_only=False):
    routes = json.loads((ROOT / 'src/routes.json').read_text(encoding='utf-8'))
    pages = {}
    for destination, source in routes.items():
        if product_only and not destination.startswith('ezvideorepair'):
            continue
        if spanish_only and not destination.endswith('_es.html'):
            continue
        pages[destination] = (ROOT / source).read_bytes()

    if check:
        stale = [name for name, data in pages.items() if not (ROOT / name).is_file() or (ROOT / name).read_bytes() != data]
        if stale:
            raise ValueError('Generated pages differ from sources: ' + ', '.join(stale))
    else:
        for name, data in pages.items():
            (ROOT / name).write_bytes(data)
    return list(pages)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify published pages without writing')
    args = parser.parse_args()
    names = build(check=args.check)
    print(f'{"Checked" if args.check else "Built"} {len(names)} pages')
