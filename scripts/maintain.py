#!/usr/bin/env python3
"""Export/check/build the bilingual resume. Python 3.9+, standard library only."""
import argparse
import copy
from datetime import date
import json
import re
import sys
from html import escape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = {'en': 'index.html', 'zh': 'index_zh.html'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Node:
    def __init__(self, tag='', attrs=(), start=0, inner=0):
        self.tag, self.attrs = tag, dict(attrs)
        self.start, self.inner, self.end_inner, self.end = start, inner, inner, inner
        self.children = []

    def has(self, cls):
        return cls in self.attrs.get('class', '').split()

    def find(self, predicate):
        return next(n for n in self.walk() if predicate(n))

    def walk(self):
        for child in self.children:
            yield child
            yield from child.walk()


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0]
        self.lines.extend(m.end() for m in re.finditer('\n', source))
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)
        self.close()
        if len(self.stack) != 1:
            raise ValueError("Unclosed HTML tag: " + self.stack[-1].tag)

    def position(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.position()
        node = Node(tag, attrs, start, start + len(self.get_starttag_text()))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            node = self.stack.pop()
            node.end = node.end_inner = node.inner

    def handle_endtag(self, tag):
        if self.stack[-1].tag != tag:
            raise ValueError(f'Unbalanced HTML tag: {tag}')
        node = self.stack.pop()
        node.end_inner = self.position()
        node.end = self.source.index('>', node.end_inner) + 1

    def inside(self, node):
        return self.source[node.inner:node.end_inner]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def list_items(doc, node):
    return [doc.inside(n) for n in node.children if n.tag == 'li']


def groups(doc, parent):
    result = []
    for i, node in enumerate(n for n in parent.children if n.tag == 'details'):
        summary = doc.inside(node.find(lambda n: n.tag == 'summary'))
        count = re.search(r'(<span class="cnt">)\d+', summary)
        if count:
            summary = summary[:count.end(1)] + '{{count}}' + summary[count.end():]
        result.append({'id': f'group-{i + 1}', 'summary_html': summary,
                       'items': [{'id': f'item-{j + 1}', 'html': value} for j, value in enumerate(
                           list_items(doc, node.find(lambda n: n.tag == 'ul')))]})
    return result


def export(root, force=False):
    """Explicit export reads HTML and replaces the JSON/template snapshot."""
    targets = [root / 'content' / 'profile' / f'{lang}.json' for lang in LOCALES]
    targets += [root / 'templates' / 'profile' / f'{lang}.html' for lang in LOCALES]
    if not force and any(p.exists() for p in targets):
        raise ValueError('Export would overwrite content/templates. Back up edits and use export --force.')
    outputs = []
    for lang, filename in LOCALES.items():
        doc = Document((root / filename).read_text(encoding='utf-8'))
        replacements = []
        def slot(node, name):
            value = doc.inside(node)
            replacements.append((node.inner, node.end_inner, '{{' + name + '}}'))
            return value
        find = doc.root.find
        title = find(lambda n: n.tag == 'title')
        # Plain title stored decoded, escaped again at build time.
        from html import unescape
        data = {'schema_version': 1, 'language': lang,
                'title': unescape(slot(title, 'title')), 'meta': {}, 'structured_data': None}
        for node in doc.root.walk():
            if node.tag == 'meta' and 'content' in node.attrs:
                kind = 'property' if 'property' in node.attrs else 'name'
                key = node.attrs.get(kind)
                if not key:
                    continue
                data['meta'][key] = node.attrs['content']
                raw = doc.source[node.start:node.inner]
                value = re.search(r'content="([^"]*)"', raw)
                if not value:
                    raise ValueError('Expected double-quoted meta content')
                replacements.append((node.start + value.start(1), node.start + value.end(1), '{{meta:' + key + '}}'))
            if node.tag == 'script' and node.attrs.get('type') == 'application/ld+json':
                data['structured_data'] = json.loads(slot(node, 'structured_data'))
        def href_slot(node, key):
            raw = doc.source[node.start:node.inner]
            match = re.search(r'href="([^"]*)"', raw)
            replacements.append((node.start + match.start(1), node.start + match.end(1), '{{' + key + '}}'))
            return node.attrs['href']
        nav = find(lambda n: n.tag == 'nav')
        data['nav'] = {'logo_html': slot(nav.find(lambda n: n.has('logo')), 'nav:logo_html'),
                       'language_label': slot(nav.find(lambda n: n.has('lang-switch')), 'nav:language_label')}
        hero = find(lambda n: n.tag == 'header')
        data['hero'] = {'heading_html': slot(hero.find(lambda n: n.tag == 'h1'), 'hero:heading_html'),
                        'role_html': slot(hero.find(lambda n: n.has('role')), 'hero:role_html'), 'links': []}
        for index, link in enumerate(n for n in hero.walk() if n.tag == 'a'):
            identifier = f'link-{index + 1}'
            prefix = 'hero:' + identifier
            svg = link.find(lambda n: n.tag == 'svg')
            label = doc.source[svg.end:link.end_inner]
            replacements.append((svg.end, link.end_inner, '{{' + prefix + ':label}}'))
            data['hero']['links'].append({'id': identifier, 'label': label.strip(),
                                         'url': href_slot(link, prefix + ':url')})
        footer = find(lambda n: n.tag == 'footer')
        copyright_node = footer.children[0].children[-1]
        data['footer'] = {'copyright_html': slot(copyright_node, 'footer:copyright_html'), 'links': []}
        for index, link in enumerate(n for n in footer.walk() if n.tag == 'a'):
            identifier = f'link-{index + 1}'
            prefix = 'footer:' + identifier
            data['footer']['links'].append({'id': identifier, 'label': slot(link, prefix + ':label'),
                                           'url': href_slot(link, prefix + ':url')})
        for section in ['experience', 'education']:
            container = find(lambda n: n.attrs.get('id') == section)
            data[section + '_label'] = slot(container.find(lambda n: n.has('kicker')), section + '_label')
            items_node = container.find(lambda n: n.has('timeline' if section == 'experience' else 'edu'))
            slot(items_node, section)
            data[section] = []
            for i, item in enumerate(items_node.children):
                record = {'id': f'{section}-{i + 1}'}
                fields = {'heading_html': lambda n: n.tag == 'h3', 'time_html': lambda n: n.has('t-time')} if section == 'experience' else {
                    'school_html': lambda n: n.has('school'), 'degree_html': lambda n: n.has('deg'), 'year_html': lambda n: n.has('yr')}
                record.update({key: doc.inside(item.find(predicate)) for key, predicate in fields.items()})
                if section == 'experience':
                    subtitle = next((n for n in item.children if n.has('t-sub')), None)
                    record['subtitle_html'] = doc.inside(subtitle) if subtitle else ''
                    ul = next(n for n in item.children if n.tag == 'ul')
                    record['bullets'] = [{'id': f'bullet-{j + 1}', 'html': value} for j, value in enumerate(list_items(doc, ul))]
                    tags = next((n for n in item.children if n.has('tag-row')), None)
                    record['tags_html'] = doc.inside(tags) if tags else ''
                record['groups'] = groups(doc, item)
                data[section].append(record)
        template = doc.source
        for start, end, replacement in sorted(replacements, reverse=True):
            template = template[:start] + replacement + template[end:]
        outputs.append((lang, data, template))
    validate_pair(outputs[0][1], outputs[1][1])
    for lang, data, template in outputs:
        dump(root / 'content' / 'profile' / f'{lang}.json', data)
        path = root / 'templates' / 'profile' / f'{lang}.html'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(template, encoding='utf-8')


def check_items(items, where):
    if not isinstance(items, list):
        raise ValueError(f'{where}: expected a list')
    ids = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f'{where}: entries must be JSON objects')
        identifier = item.get('id')
        if not isinstance(identifier, str) or not identifier:
            raise ValueError(f'{where}: every entry needs a non-empty id')
        ids.append(identifier)
    if len(set(ids)) != len(ids):
        raise ValueError(f'{where}: duplicate id')
    return ids


def validate_pair(en, zh):
    def shape(data, lang):
        if data['schema_version'] != 1 or data['language'] != lang:
            raise ValueError(f'{lang}: wrong schema_version or language')
        for key in ['title', 'experience_label', 'education_label']:
            if not isinstance(data[key], str):
                raise ValueError(f'{lang}.{key}: expected a string')
        if not isinstance(data['meta'], dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in data['meta'].items()):
            raise ValueError('meta must contain string keys and values')
        result = []
        for owner in ['hero', 'footer']:
            result.append((owner, check_items(data[owner]['links'], owner)))
            for link in data[owner]['links']:
                if not all(isinstance(link[k], str) for k in ['url', 'label']):
                    raise ValueError('Link label/url must be strings')
        for section in ['experience', 'education']:
            entries = data[section]
            check_items(entries, lang + '.' + section)
            for entry in entries:
                group_shapes = []
                check_items(entry['groups'], entry['id'] + '.groups')
                for group in entry['groups']:
                    group_shapes.append((group['id'], check_items(group['items'], group['id'])))
                    if not isinstance(group['summary_html'], str):
                        raise ValueError('summary_html must be a string')
                    for item in group['items']:
                        if not isinstance(item['html'], str):
                            raise ValueError('item html must be a string')
                fields = ['heading_html', 'time_html', 'tags_html', 'subtitle_html'] if section == 'experience' else ['school_html', 'degree_html', 'year_html']
                for field in fields:
                    if not isinstance(entry[field], str):
                        raise ValueError(f'{entry["id"]}.{field}: expected a string')
                bullets = check_items(entry['bullets'], entry['id']) if section == 'experience' else []
                if section == 'experience' and any(not isinstance(b['html'], str) for b in entry['bullets']):
                    raise ValueError('bullet html must be a string')
                result.append((entry['id'], bullets, group_shapes))
        return result
    if shape(en, 'en') != shape(zh, 'zh'):
        raise ValueError('Bilingual structure differs: keep entry/group/item/bullet IDs and order identical in en.json and zh.json.')
    if en['meta'].keys() != zh['meta'].keys():
        raise ValueError('Bilingual meta fields differ')


def render_groups(groups):
    output = ''
    for group in groups:
        summary = group['summary_html'].replace('{{count}}', str(len(group['items'])))
        output += '        <details class="fold" open>\n          <summary>' + summary + '</summary>\n          <ul class="fold-list">\n'
        output += ''.join('            <li>' + item['html'] + '</li>\n' for item in group['items'])
        output += '          </ul>\n        </details>\n'
    return output


def render_section(data, section):
    output = '\n'
    for i, entry in enumerate(data[section]):
        if section == 'experience':
            cls = 't-item reveal' if i == 0 else 't-item past reveal'
            output += f'      <div class="{cls}">\n        <div class="t-head">\n          <h3>{entry["heading_html"]}</h3>\n          <span class="t-time">{entry["time_html"]}</span>\n        </div>\n'
            if entry['subtitle_html']:
                output += '        <div class="t-sub">' + entry['subtitle_html'] + '</div>\n'
            output += '        <ul>\n'
            output += ''.join('          <li>' + b['html'] + '</li>\n' for b in entry['bullets'])
            output += '        </ul>\n' + render_groups(entry['groups'])
            if entry['tags_html']:
                output += '        <div class="tag-row">' + entry['tags_html'] + '</div>\n'
        else:
            output += '      <div class="card reveal">\n'
            for key, cls in [('school_html', 'school'), ('degree_html', 'deg'), ('year_html', 'yr')]:
                output += f'        <div class="{cls}">{entry[key]}</div>\n'
            output += render_groups(entry['groups'])
        output += '      </div>\n'
    return output + '    '


def render(data, template):
    values = {k: data[k] for k in ['experience_label', 'education_label']}
    for owner, keys in {'nav': ['logo_html', 'language_label'], 'hero': ['heading_html', 'role_html'], 'footer': ['copyright_html']}.items():
        for key in keys:
            values[owner + ':' + key] = data[owner][key]
    for owner in ['hero', 'footer']:
        for link in data[owner]['links']:
            prefix = owner + ':' + link['id']
            values[prefix + ':url'] = escape(link['url'], quote=True)
            values[prefix + ':label'] = escape(link['label'])

    values['title'] = escape(data['title'], quote=False)
    structured = copy.deepcopy(data['structured_data'])
    if not isinstance(structured, dict):
        raise ValueError('structured_data must be a JSON object')
    for node in structured.get('@graph', []):
        if node.get('@type') == 'ProfilePage':
            node['name'] = data['title']
            node['description'] = data['meta']['description']
    values['structured_data'] = '\n' + json.dumps(structured, ensure_ascii=False, indent=2).replace('<', '\\u003c') + '\n'
    meta = dict(data['meta'])
    # The page title/description are authoritative for social previews as well.
    for key in ['og:title', 'twitter:title']:
        meta[key] = data['title']
    for key in ['og:description', 'twitter:description']:
        meta[key] = meta['description']
    values.update({'meta:' + k: escape(v, quote=True) for k, v in meta.items()})
    for owner in ['hero', 'footer']:
        expected = set(re.findall(r'\{\{' + owner + r':([^:{}]+):url\}\}', template))
        if expected != {link['id'] for link in data[owner]['links']}:
            raise ValueError(f'{owner}: link IDs must match template slots; edit templates when adding/removing icon links')
    expected_meta = set(re.findall(r'\{\{meta:([^{}]+)\}\}', template))
    if expected_meta != set(meta):
        raise ValueError('Meta keys must match template slots')
    values.update({key: render_section(data, key) for key in ['experience', 'education']})
    def replace(match):
        if match[1] not in values:
            raise ValueError('Unknown template slot: ' + match[1])
        return values[match[1]]
    page = re.sub(r'\{\{([^{}]+)\}\}', replace, template)
    Document(page)  # Fail before either file is written if markup is unbalanced.
    return page


def build(root, content_dir=None, output_dir=None, check=False):
    content_dir = content_dir or root / 'content' / 'profile'
    data = {lang: load(content_dir / f'{lang}.json') for lang in LOCALES}
    validate_pair(data['en'], data['zh'])
    # Render and validate BOTH languages before writing either output.
    pages = {name: render(data[lang], (root / 'templates' / 'profile' / f'{lang}.html').read_text(encoding='utf-8')) for lang, name in LOCALES.items()}
    if not check:
        output_dir = output_dir or root
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, page in pages.items():
            path = output_dir / name
            temporary = path.with_suffix('.html.tmp')
            temporary.write_text(page, encoding='utf-8')
            temporary.replace(path)
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['export', 'check', 'build'])
    parser.add_argument('--force', action='store_true', help='Allow export to overwrite JSON/templates')
    parser.add_argument('--content-dir', type=Path, help='Input folder containing en.json and zh.json')
    parser.add_argument('--output-dir', type=Path, help='Write previews here instead of site root')
    args = parser.parse_args()
    try:
        if args.command == 'export':
            export(ROOT, args.force)
        else:
            build(ROOT, args.content_dir, args.output_dir, args.command == 'check')
        if args.command == 'build' and (args.output_dir is None or args.output_dir.resolve() == ROOT):
            memory = ROOT / 'MEMORY.md'
            if memory.exists():
                counts = load((args.content_dir or ROOT / 'content' / 'profile') / 'en.json')
                note = f'\n### {date.today().isoformat()}：通过 JSON 生成双语页面\n- 运行 scripts/maintain.py build，双语结构及 HTML 检查通过，更新 index.html 与 index_zh.html；工作经历 {len(counts["experience"])} 项、教育 {len(counts["education"])} 项。具体修改见 content/profile/en.json 和 content/profile/zh.json 的 Git 差异。\n'
                memory.write_text(memory.read_text(encoding='utf-8') + note, encoding='utf-8')
        print(args.command + ': OK (en + zh)')
    except (ValueError, KeyError, TypeError, OSError, StopIteration) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
