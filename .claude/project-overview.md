# Project Overview — czymh.github.io

Zhao Chen's personal academic homepage, hosted on GitHub Pages.

## Status (2024-06-22, refactor)

Rebuilt from Hexo-generated static output into a **hand-written single-page static site** (no build step, no Hexo source).

## Structure

```
index.html          single-page site (Hero / About / Publications / Projects / Figures / Teaching / Contact)
css/style.css       all styles (dark deep-space theme, green accent, CSS variables)
js/main.js          vanilla JS (mobile nav, scroll reveal, figure lightbox) — no dependencies
404.html            custom 404
robots.txt          allow-all + sitemap pointer
sitemap.xml         single-URL sitemap
img/                favicon.png, myprofile.png (avatar), wholefield.png (hero banner / simulation field)
attaches/CV.pdf     placeholder CV ("This is a detail resume in PDF for test.") — needs real CV
```

## Design system

- Dark theme: `--bg #0b0e10`, `--surface #141a1f`, text `#e6e9ec`, accent green `#34d399`
- Fonts: Spectral (display) + IBM Plex Sans (body) + IBM Plex Mono (labels), via Google Fonts
- Spacing on 8px scale; single page, anchor navigation, responsive (≤720px mobile nav)

## Publications auto-sync (NASA ADS)

Publications render from `data/publications.json`, which is the single source of truth for the section.

- **Sync script**: `.github/scripts/sync_publications.py` — fetches the ADS library
  `HtElQUxPQDWHA8aZ5Pl3xg` (GET /v1/library → bibcodes; POST /v1/search/query → metadata),
  normalizes author names, writes `data/publications.json`.
- **Workflow**: `.github/workflows/sync-publications.yml` — runs weekly (Mon 04:23 UTC) and
  on `workflow_dispatch`; commits the JSON only when changed.
- **Secret needed**: `ADS_API_TOKEN` (GitHub Actions secret) — user must create it at
  https://ui.adsabs.harvard.edu/user/settings/token.
- **Site rendering**: `js/main.js` fetches `data/publications.json` and replaces `#pub-list`
  (max 5 authors, **Zhao Chen** bolded, `et al.` when truncated). The static `<ol>` in
  `index.html` is the no-JS fallback.
- **Seed**: `data/publications.json` currently seeded with 8 papers (bibcodes blank except
  2022MNRAS.516.6210P); the first real workflow run fills real bibcodes.

## Source of truth

Content (name, affiliation, 8 publications, projects) drafted from public sources:
- GitHub: https://github.com/czymh
- ORCID: https://orcid.org/0000-0002-2183-9863
- RTD docs: csst-emulator / kunsimulation

## TODOs (owner: user)

- Provide real simulation figures for the gallery + project thumbnails (currently placeholders)
- Confirm email (chiyiru@sjtu.edu.cn) and exact CSST green
- Add author lists to publications (currently omitted)
- Replace placeholder CV.pdf and FastPM-mocks description
