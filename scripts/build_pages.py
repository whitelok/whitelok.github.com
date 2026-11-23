"""Publish maintained static page sources to their existing public URLs."""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DemoVideo(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'video' and attributes.get('id') == 'flume-recording':
            src = attributes.get('src') or ''
            self.sources.append(src.split('?', 1)[0].split('#', 1)[0].removeprefix('/'))


def check_product_demo(source, data):
    expected = f'assets/products/ezvideorepair/usgs-flume/ui-demo-{source.stem}.mp4'
    video = DemoVideo()
    video.feed(data.decode('utf-8'))
    video.close()
    if video.sources != [expected]:
        raise ValueError(f'{source}: expected the primary demo video to use {expected}')
    if not (ROOT / expected).is_file():
        raise ValueError(f'{source}: missing demo file {expected}')


def build(check=False, product_only=False, spanish_only=False):
    routes = json.loads((ROOT / 'src/routes.json').read_text(encoding='utf-8'))
    pages = {}
    for destination, source in routes.items():
        if product_only and not destination.startswith('ezvideorepair'):
            continue
        if spanish_only and not destination.endswith('_es.html'):
            continue
        source = Path(source)
        pages[destination] = (ROOT / source).read_bytes()
        if check and source.parent == Path('src/pages/ezvideorepair/product'):
            check_product_demo(source, pages[destination])

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
