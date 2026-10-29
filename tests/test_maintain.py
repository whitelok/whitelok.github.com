"""Run with: python3 -m unittest discover -s tests -v"""
import copy
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('maintain', ROOT / 'scripts/maintain.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Tokens(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.tokens = []
        self.in_json = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tokens.append(('start', tag, sorted(attrs)))
        if tag == 'script' and dict(attrs).get('type') == 'application/ld+json':
            self.in_json = True

    def handle_endtag(self, tag):
        self.tokens.append(('end', tag))
        if tag == 'script':
            self.in_json = False

    def handle_data(self, data):
        if self.in_json:
            self.tokens.append(('json', json.loads(data)))
        elif data.strip():
            self.tokens.append(('text', re.sub(r'\s+', ' ', data).strip()))


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ['content', 'templates']:
            shutil.copytree(ROOT / directory, self.root / directory)
        for filename in m.LOCALES.values():
            shutil.copy(ROOT / filename, self.root / filename)

    def edit(self, lang, callback):
        path = self.root / 'content' / 'profile' / f'{lang}.json'
        data = m.load(path)
        callback(data)
        m.dump(path, data)

    def test_export_round_trip_preserves_html_tokens_and_assets(self):
        m.export(self.root, force=True)
        pages = m.build(self.root, check=True)
        for filename, page in pages.items():
            self.assertEqual(Tokens((self.root / filename).read_text()).tokens, Tokens(page).tokens)

    def test_real_json_matches_current_pages(self):
        for filename, page in m.build(self.root, check=True).items():
            self.assertEqual(Tokens((self.root / filename).read_text()).tokens, Tokens(page).tokens)

    def test_update_heading_and_title(self):
        for lang in m.LOCALES:
            self.edit(lang, lambda d: d.update(title='New title & research'))
            self.edit(lang, lambda d: d['hero'].update(role_html='New <b>role</b>'))
        page = m.build(self.root, check=True)['index.html']
        self.assertIn('<title>New title &amp; research</title>', page)
        self.assertIn('content="New title &amp; research"', page)
        self.assertIn('New <b>role</b>', page)

    def test_add_paper_updates_both_counts(self):
        original_count = len(m.load(self.root / 'content' / 'profile' / 'en.json')['experience'][0]['groups'][0]['items'])
        for lang in m.LOCALES:
            self.edit(lang, lambda d: d['experience'][0]['groups'][0]['items'].insert(0, {'id': 'new-paper', 'html': '<a href="https://example.com/">New paper</a>'}))
        pages = m.build(self.root, check=True)
        self.assertIn(f'{original_count + 1} papers', pages['index.html'])
        self.assertIn(f'{original_count + 1} 篇', pages['index_zh.html'])
        self.assertIn('New paper', pages['index.html'])

    def test_bilingual_mismatch_writes_neither_page(self):
        before = {f: (self.root / f).read_bytes() for f in m.LOCALES.values()}
        self.edit('en', lambda d: d['experience'][0]['bullets'].pop())
        with self.assertRaisesRegex(ValueError, 'Bilingual structure differs'):
            m.build(self.root)
        for filename, source in before.items():
            self.assertEqual(source, (self.root / filename).read_bytes())

    def test_duplicate_id_rejected(self):
        self.edit('en', lambda d: d['experience'].append(copy.deepcopy(d['experience'][0])))
        with self.assertRaisesRegex(ValueError, 'duplicate id'):
            m.build(self.root)

    def test_invalid_html_in_second_language_does_not_write_first(self):
        before = (self.root / 'index.html').read_bytes()
        self.edit('zh', lambda d: d['hero'].update(role_html='<b>unclosed'))
        with self.assertRaises(ValueError):
            m.build(self.root)
        self.assertEqual(before, (self.root / 'index.html').read_bytes())

    def test_check_and_preview_leave_source_pages_untouched(self):
        before = (self.root / 'index.html').read_bytes()
        m.build(self.root, check=True)
        m.build(self.root, output_dir=self.root / 'preview')
        self.assertEqual(before, (self.root / 'index.html').read_bytes())
        self.assertTrue((self.root / 'preview/index_zh.html').is_file())

    def test_export_requires_explicit_overwrite(self):
        with self.assertRaisesRegex(ValueError, '--force'):
            m.export(self.root)

    def test_links_not_silently_ignored(self):
        for lang in m.LOCALES:
            self.edit(lang, lambda d: d['hero']['links'].append({'id': 'new-link', 'label': 'New', 'url': 'https://example.com/'}))
        with self.assertRaisesRegex(ValueError, 'link IDs must match template'):
            m.build(self.root)


if __name__ == '__main__':
    unittest.main()
