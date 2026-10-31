import json
import unittest
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__();self.ids=[];self.assets=[];self.links=[];self.structure=[];self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs);self.structure.append((tag,sorted(attrs)))
        if "id" in attrs:self.ids.append(attrs["id"])
        if tag=="a":self.links.append(attrs)
        if tag in ["img","script"]:self.assets.append(attrs["src"])
        if tag=="link" and attrs.get("rel")=="stylesheet":self.assets.append(attrs["href"])
class ProductPageTests(unittest.TestCase):
    def test_bilingual_structure_and_sources_match(self):
        zh=json.loads((ROOT/"content/ezvideorepair/zh.json").read_text())
        en=json.loads((ROOT/"content/ezvideorepair/en.json").read_text())
        self.assertEqual(zh.keys(),en.keys())
        a=Page((ROOT/"ezvideorepair.html").read_text());b=Page((ROOT/"ezvideorepair_en.html").read_text())
        self.assertEqual(a.structure,b.structure)
        self.assertEqual(a.ids,b.ids)
        for field in ["features","workflow","requirements","faq"]:self.assertEqual(len(zh[field]),len(en[field]))
    def test_links_assets_and_no_placeholder_downloads(self):
        for name in ["ezvideorepair.html","ezvideorepair_en.html"]:
            html=(ROOT/name).read_text();page=Page(html)
            self.assertEqual(len(page.ids),len(set(page.ids)))
            self.assertNotIn("$",html)
            for src in page.assets:self.assertTrue((ROOT/urlsplit(src).path).is_file(),src)
            for link in page.links:
                href=link.get("href","")
                if href.startswith("#") and href!="#":self.assertIn(href[1:],page.ids)
                if link.get("target")=="_blank":self.assertIn("noopener",link.get("rel",""))
                self.assertNotIn("apps.apple.com",href)
                self.assertFalse(href.endswith((".dmg",".pkg")))
            self.assertIn("https://github.com/whitelok/EZVideoRepair",html)
            self.assertIn("https://huggingface.co/whitelok/seedvr2-hybricprecision-3b",html)
if __name__=="__main__":unittest.main()
