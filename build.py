"""Build a small bilingual site. Content is plain Markdown; no JS is required to read it."""
from __future__ import annotations
import argparse
import json
import re
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markdown_it import MarkdownIt
from markupsafe import Markup
import yaml

ROOT = Path(__file__).resolve().parent
MD = MarkdownIt('commonmark', {'html': False, 'breaks': False}).enable('table')

def read_posts(root: Path, lang: str) -> list[dict]:
    posts = []
    for path in sorted((root / 'content' / lang).glob('*.md')):
        text = path.read_text(encoding='utf-8')
        if not text.startswith('---\n') or '\n---\n' not in text[4:]:
            raise ValueError(f'Missing frontmatter: {path.name}')
        raw, body = text[4:].split('\n---\n', 1)
        meta = yaml.safe_load(raw)
        if not isinstance(meta, dict):
            raise ValueError(f'Invalid frontmatter: {path.name}')
        if meta.get('publish') is not True:
            continue
        if meta.get('sensitive') is not False:
            raise ValueError(f'Sensitive article cannot be published: {path.name}')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', path.stem):
            raise ValueError(f'Invalid slug: {path.stem}')
        for key in ('title', 'description', 'category'):
            if not isinstance(meta.get(key), str) or not meta[key].strip():
                raise ValueError(f'Missing {key}: {path.name}')
        published = date.fromisoformat(str(meta['date']))
        prefix = '/' if lang == 'en' else '/zh/'
        words = len(re.findall(r'[\u4e00-\u9fff]|\b[\w-]+\b', body))
        posts.append({**meta, 'date': published.isoformat(), 'slug': path.stem,
                      'url': f'{prefix}notes/{path.stem}/', 'html': Markup(MD.render(body)),
                      'minutes': max(1, round(words / (350 if lang == 'zh' else 200)))})
    return sorted(posts, key=lambda item: (item['date'], item['slug']), reverse=True)

def build(root: Path = ROOT, output: Path | None = None) -> Path:
    root = root.resolve()
    output = output or root / 'dist'
    # Only a fixed generated directory may be replaced; preserve previous builds.
    if output.absolute() != root / 'dist' or output.is_symlink() or (hasattr(output, 'is_junction') and output.is_junction()):
        raise ValueError('Build output must be the local dist directory, without links')
    site = json.loads((root / 'site.json').read_text(encoding='utf-8'))
    if site.get('publish') is not True or site.get('sensitive') is not False:
        raise ValueError('The site must explicitly opt in to publication')
    if not site['url'].startswith('https://'):
        raise ValueError('The canonical URL must use HTTPS')
    env = Environment(loader=FileSystemLoader(root / 'templates'), autoescape=select_autoescape(['html', 'xml']), undefined=StrictUndefined)
    posts = {lang: read_posts(root, lang) for lang in ('en', 'zh')}
    rendered = {}
    routes = []
    for lang in ('en', 'zh'):
        prefix = '/' if lang == 'en' else '/zh/'
        other = 'zh' if lang == 'en' else 'en'
        other_prefix = '/zh/' if lang == 'en' else '/'
        t = site['languages'][lang]
        context = {'site': site, 'lang': lang, 'html_lang': 'en' if lang == 'en' else 'zh-CN', 't': t,
                   'home': prefix, 'notebook': prefix + 'notes/', 'posts': posts[lang], 'year': site['updated'][:4]}
        def page(template, route, title, description, alternate, **extras):
            values = {**context, 'route': route, 'title': title, 'description': description,
                      'alternate': alternate, 'other_lang': other, 'is_home': route == prefix,
                      'is_404': False, 'article': None, **extras}
            name = route.lstrip('/') + 'index.html'
            if route == '/404.html':
                name = '404.html'
            rendered[name] = env.get_template(template).render(**values)
            if not values['is_404']:
                routes.append(route)
        page('home.html', prefix, t['name'] + (' · Power systems & learning' if lang == 'en' else ' · 电力系统与学习'), t['description'], other_prefix)
        page('notebook.html', prefix + 'notes/', t['nav']['notebook'] + ' · ' + t['name'], t['notebook_intro'], other_prefix + 'notes/')
        other_posts = {p['slug']: p for p in posts[other]}
        for post in posts[lang]:
            alt = other_posts.get(post['slug'])
            page('article.html', post['url'], post['title'] + ' · ' + t['name'], post['description'], alt['url'] if alt else None, article=post)
        if lang == 'en':
            page('404.html', '/404.html', 'Page not found · Zicheng Wang', t['description'], '/zh/', is_404=True)
        rss = ET.Element('rss', version='2.0')
        channel = ET.SubElement(rss, 'channel')
        for key, value in [('title', t['name'] + ' · ' + t['nav']['notebook']), ('link', site['url'] + prefix + 'notes/'), ('description', t['notebook_intro']), ('language', lang)]:
            ET.SubElement(channel, key).text = value
        for post in posts[lang]:
            item = ET.SubElement(channel, 'item')
            for key, value in [('title', post['title']), ('link', site['url'] + post['url']), ('guid', site['url'] + post['url']), ('description', post['description']), ('pubDate', datetime.fromisoformat(post['date']).replace(tzinfo=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'))]:
                ET.SubElement(item, key).text = value
        rendered[prefix.lstrip('/') + 'feed.xml'] = ET.tostring(rss, encoding='unicode', xml_declaration=True)
    sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for route in sorted(routes):
        entry = ET.SubElement(sitemap, 'url')
        ET.SubElement(entry, 'loc').text = site['url'] + route
    rendered['sitemap.xml'] = ET.tostring(sitemap, encoding='unicode', xml_declaration=True)
    rendered['robots.txt'] = f'User-agent: *\nAllow: /\nSitemap: {site["url"]}/sitemap.xml\n'
    rendered['.nojekyll'] = ''
    if output.exists():
        history = root / '.build-history' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        history.mkdir(parents=True, exist_ok=True)
        shutil.move(str(output), str(history / 'dist'))
    output.mkdir(parents=True)
    shutil.copytree(root / 'assets', output / 'assets')
    for name, text in rendered.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + '\n', encoding='utf-8')
    return output

if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    result = build()
    print(f'Built {len(list(result.rglob("*.html")))} pages → {result}')
