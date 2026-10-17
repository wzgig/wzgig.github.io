"""Behavioral checks for routing, safe rendering, and withdrawn content."""
import importlib.util
import json
import shutil
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('site_builder', ROOT / 'build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for name in ('href', 'src'):
            if name in attrs:
                self.urls.append(attrs[name])

class SiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'site'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', 'dist', '.build-history', '.venv', '__pycache__', 'test-results'))
    def tearDown(self):
        self.temp.cleanup()
    def test_routes_translations_and_links(self):
        dist = builder.build(self.root)
        for path in dist.rglob('*.html'):
            page = Links()
            text = path.read_text(encoding='utf-8')
            page.feed(text)
            self.assertIn('<h1', text)
            self.assertIn('id="main"', text)
            for url in page.urls:
                parsed = urlsplit(url)
                if parsed.scheme or parsed.netloc:
                    continue
                target = dist / unquote(parsed.path).lstrip('/') if parsed.path else path
                if target.is_dir():
                    target /= 'index.html'
                self.assertTrue(target.is_file(), f'{path}: {url}')
                if parsed.fragment:
                    linked = Links()
                    linked.feed(target.read_text(encoding='utf-8'))
                    self.assertIn(parsed.fragment, linked.ids, f'{path}: {url}')
        self.assertIn('<html lang="en">', (dist / 'index.html').read_text(encoding='utf-8'))
        self.assertIn('<html lang="zh-CN">', (dist / 'zh/index.html').read_text(encoding='utf-8'))
        for name in ('feed.xml', 'zh/feed.xml', 'sitemap.xml'):
            ET.parse(dist / name)
    def test_withdrawal_removes_page_and_preserves_previous_build(self):
        dist = builder.build(self.root)
        post = self.root / 'content/en/from-models-to-circuits.md'
        post.write_text(post.read_text(encoding='utf-8').replace('publish: true', 'publish: false'), encoding='utf-8')
        builder.build(self.root)
        self.assertFalse((dist / 'notes/from-models-to-circuits/index.html').exists())
        self.assertTrue(list((self.root / '.build-history').glob('*/dist/notes/from-models-to-circuits/index.html')))
        zh = (dist / 'zh/notes/from-models-to-circuits/index.html').read_text(encoding='utf-8')
        self.assertNotIn('class="language"', zh)
    def test_sensitive_content_fails_before_replacing_build(self):
        dist = builder.build(self.root)
        previous = (dist / 'index.html').read_bytes()
        post = self.root / 'content/en/from-models-to-circuits.md'
        post.write_text(post.read_text(encoding='utf-8').replace('sensitive: false', 'sensitive: true'), encoding='utf-8')
        with self.assertRaises(ValueError):
            builder.build(self.root)
        self.assertEqual(previous, (dist / 'index.html').read_bytes())
    def test_raw_html_is_escaped(self):
        post = self.root / 'content/en/from-models-to-circuits.md'
        with post.open('a', encoding='utf-8') as f:
            f.write('\n<script>alert(1)</script>\n')
        dist = builder.build(self.root)
        page = (dist / 'notes/from-models-to-circuits/index.html').read_text(encoding='utf-8')
        self.assertNotIn('<script>alert', page)
        self.assertIn('&lt;script&gt;', page)

if __name__ == '__main__':
    unittest.main()
