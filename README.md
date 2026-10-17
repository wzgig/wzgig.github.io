# Zicheng Wang · Personal website

An English-first, bilingual academic home for research, publications, projects, and notes. Chinese pages live at `/zh/`. Plain Markdown and one JSON file hold the content; Python generates complete HTML pages.

## Local preview

Use Python 3.12 or later in this repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe build.py
.\.venv\Scripts\python.exe -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Open `http://127.0.0.1:4173/`. Stop the server with Ctrl+C. Preview over HTTP: root-relative links are designed for GitHub Pages, not `file://`.

## Update content

| Change | File |
| --- | --- |
| Biography, education, honors, navigation, links | `site.json` |
| Papers and projects | `papers` and `projects` in `site.json` |
| English notes | `content/en/<slug>.md` |
| Chinese notes | `content/zh/<slug>.md` |
| Colors, spacing, typography | `assets/styles.css` |
| Page structure | `templates/` |
| Portrait and social preview | `assets/portrait.webp`, `assets/social.webp` |

The author's editing master is maintained separately; this repository is the reviewed public export. Apply lasting edits to that master before exporting again. If editing this repository directly on GitHub, reconcile those edits with the master before the next export.

Use the same filename for two translations. If a translation is absent, the article does not show a misleading language switch. Untranslated notes still appear in their own language's index. A new note needs this frontmatter:

```yaml
---
title: A clear title
description: A short description for readers and search engines.
date: 2026-10-18
category: Research notes
publish: true
sensitive: false
---
```

Write standard Markdown below it. Use `##` for sections; the template supplies the page title. Raw HTML is escaped. `publish: false` omits a note from the build, but does **not** hide source files already committed to a public repository: never commit private drafts here. Withdrawing a public page cannot erase prior Git history or third-party copies.

## Deployment

For `wzgig/wzgig.github.io`, open **GitHub → repository → Settings → Pages → Build and deployment → Source → GitHub Actions**. The workflow tests and builds on pushes to `main`, then uploads only `dist/`. The public address is `https://wzgig.github.io/`.

The existing `https://wzgig.github.io/Resume/` project remains the CV destination. No custom domain is configured. For another domain, update `url` in `site.json` and the Pages settings together.

Every build starts with a fresh `dist/` so withdrawn articles cannot linger. Previous local builds are moved into ignored `.build-history/`; review that folder periodically if disk space becomes a concern. No original source is removed by the build.

## Design and maintenance

- Static HTML; navigation, language switching, and articles work without JavaScript.
- Optional JavaScript controls the mobile menu and locally saved light/dark preference.
- No analytics, cookies, external runtime, or remotely loaded fonts.
- Canonical and language links, social previews, sitemap, RSS feeds, and a 404 page are generated automatically.
- Lora and DM Sans are self-hosted under the SIL Open Font License; licenses are in `assets/fonts/`.
- Layout inspiration: [Bendong Tan's academic site](https://tanbendong.github.io/), with an original visual implementation.
- [al-folio](https://github.com/alshedivat/al-folio) and [Academic Pages](https://github.com/academicpages/academicpages.github.io) are useful references for larger publication collections; this site keeps a smaller build and editing surface.

The personal PowerMCP repository is a working fork of [Power-Agent/PowerMCP](https://github.com/Power-Agent/PowerMCP); attribution is displayed on the site. Publications link to publisher pages. The photograph, text, and site-specific implementation are not licensed for unrestricted reuse; font licenses apply to their respective files.
