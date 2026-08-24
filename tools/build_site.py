#!/usr/bin/env python3
"""Generate the on-site article archive from articles.json."""

import json, os, re
from datetime import datetime
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = "https://sagart-cactus.github.io"
ARTS = json.load(open(os.path.join(HERE, "articles.json")))

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'"
           "%3E%3Crect width='64' height='64' rx='14' fill='%239c3d17'/%3E%3Ctext x='32' y='44' "
           "font-family='Georgia,serif' font-size='34' font-weight='700' text-anchor='middle' "
           "fill='%23fcfcfa'%3EST%3C/text%3E%3C/svg%3E")

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400'
         '&display=swap">')

THEME_SCRIPT = """<script>
  try {
    var t = localStorage.getItem('theme');
    if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
  } catch (e) {}
</script>"""

TOGGLE = """      <button class="toggle" type="button" id="theme-toggle" aria-label="Switch to dark theme" title="Switch theme">
        <svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
             stroke-linecap="round" aria-hidden="true" focusable="false">
          <circle cx="12" cy="12" r="4.2"/>
          <path d="M12 2.4v2.2M12 19.4v2.2M4.2 4.2l1.6 1.6M18.2 18.2l1.6 1.6M2.4 12h2.2M19.4 12h2.2M4.2 19.8l1.6-1.6M18.2 5.8l1.6-1.6"/>
        </svg>
        <svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
             stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
          <path d="M20.5 14.6A8.6 8.6 0 1 1 9.4 3.5a7 7 0 0 0 11.1 11.1z"/>
        </svg>
      </button>"""

TOGGLE_JS = """<script>
(function () {
  var root = document.documentElement;
  var btn = document.getElementById('theme-toggle');
  var media = window.matchMedia('(prefers-color-scheme: dark)');
  function isDark() {
    var set = root.getAttribute('data-theme');
    return set ? set === 'dark' : media.matches;
  }
  function syncLabel() {
    btn.setAttribute('aria-label', 'Switch to ' + (isDark() ? 'light' : 'dark') + ' theme');
  }
  btn.addEventListener('click', function () {
    var next = isDark() ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
    syncLabel();
  });
  media.addEventListener('change', function () {
    if (!root.getAttribute('data-theme')) syncLabel();
  });
  syncLabel();
})();
</script>"""


def iso(d):
    return datetime.strptime(d, "%b %d, %Y").strftime("%Y-%m-%d")


def pretty(d):
    dt = datetime.strptime(d, "%b %d, %Y")
    return dt.strftime("%-d %B %Y")


def page(title, desc, canonical, body, depth, extra_head="", jsonld=""):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="author" content="Sagar Trivedi">
<link rel="canonical" href="{canonical}">

<meta property="og:type" content="article">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(desc)}">

<meta name="theme-color" content="#fcfcfa" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#131313" media="(prefers-color-scheme: dark)">

<link rel="icon" href="{FAVICON}">

{FONTS}
<link rel="stylesheet" href="{up}assets/site.css">
{extra_head}
{THEME_SCRIPT}
</head>

<body>
<a class="skip" href="#main">Skip to content</a>

<div class="wrap">
{body}
</div>

{TOGGLE_JS}
{jsonld}
</body>
</html>
"""


def build_article(a, prev, nxt):
    d = depth = 2
    up = "../" * d
    nav = []
    if prev:
        nav.append(f'<a class="prevnext prev" href="{up}articles/{prev["slug"]}/">'
                   f'<span class="dir">Previous</span>{escape(prev["title"])}</a>')
    if nxt:
        nav.append(f'<a class="prevnext next" href="{up}articles/{nxt["slug"]}/">'
                   f'<span class="dir">Next</span>{escape(nxt["title"])}</a>')
    nav_html = f'<nav class="prevnext-wrap" aria-label="More in this series">{"".join(nav)}</nav>' if nav else ""

    body = f"""  <header class="page-head">
    <div class="masthead">
      <a class="backlink" href="{up}articles/">Writing</a>
{TOGGLE}
    </div>
  </header>

  <main id="main">
    <article class="post">
      <h1>{escape(a['title'])}</h1>
      <p class="post-meta">
        <time datetime="{iso(a['date'])}">{pretty(a['date'])}</time>
        <span class="dot">·</span>{a['minutes']} min read
      </p>

      <div class="post-body">
{a['html']}
      </div>

      <p class="source">Originally published on
        <a href="{a['source_url']}" rel="nofollow">LinkedIn</a>.</p>
    </article>
{nav_html}
  </main>

  <footer>
    <p><a href="{up}">Sagar Trivedi</a> · Applied AI Architect</p>
    <nav aria-label="Site">
      <a href="{up}">Resume</a>
      <a href="{up}articles/">Writing</a>
    </nav>
  </footer>"""

    canonical = f"{SITE}/articles/{a['slug']}/"
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": a["title"],
        "datePublished": iso(a["date"]),
        "description": a["excerpt"],
        "wordCount": a["words"],
        "url": canonical,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "author": {"@type": "Person", "name": "Sagar Trivedi",
                   "url": f"{SITE}/"},
    }, indent=2)
    jsonld = f'<script type="application/ld+json">\n{jsonld}\n</script>'

    return page(f"{a['title']} · Sagar Trivedi", a["excerpt"], canonical,
                body, depth, jsonld=jsonld)


def build_index(groups):
    parts = []
    for name, items in groups.items():
        rows = []
        for a in items:
            rows.append(f"""          <li>
            <a class="entry" href="{a['slug']}/">
              <span class="entry-title">{escape(a['title'])}</span>
              <span class="entry-meta"><time datetime="{iso(a['date'])}">{pretty(a['date'])}</time>
                <span class="dot">·</span>{a['minutes']} min</span>
            </a>
            <p class="entry-excerpt">{escape(a['excerpt'])}…</p>
          </li>""")
        parts.append(f"""      <section class="group" aria-labelledby="g-{abs(hash(name)) % 99999}">
        <h2 id="g-{abs(hash(name)) % 99999}">{escape(name)}</h2>
        <ul class="entries">
{chr(10).join(rows)}
        </ul>
      </section>""")

    total = sum(len(v) for v in groups.values())
    words = sum(a["words"] for v in groups.values() for a in v)

    body = f"""  <header class="page-head">
    <div class="masthead">
      <a class="backlink" href="../">Sagar Trivedi</a>
{TOGGLE}
    </div>
    <h1>Writing</h1>
    <p class="lede">I write about the parts of AI systems that decide whether they survive
    production: evaluation, failure modes, cost, and the protocols and tooling underneath.
    {total} articles, about {words // 1000},000 words.</p>
  </header>

  <main id="main">
{chr(10).join(parts)}
  </main>

  <footer>
    <p><a href="../">Sagar Trivedi</a> · Applied AI Architect</p>
    <nav aria-label="Site">
      <a href="../">Resume</a>
      <a href="https://www.linkedin.com/in/sagartrivedi/recent-activity/articles/">LinkedIn</a>
    </nav>
  </footer>"""

    return page("Writing · Sagar Trivedi",
                f"{total} articles on LLM evaluation, agent architecture, "
                "the Model Context Protocol, and agent tooling.",
                f"{SITE}/articles/", body, 1)


def main():
    groups = {}
    for a in ARTS:
        groups.setdefault(a["group"], []).append(a)

    os.makedirs(f"{ROOT}/articles", exist_ok=True)
    os.makedirs(f"{ROOT}/assets", exist_ok=True)

    # article pages, with prev/next inside each group
    for name, items in groups.items():
        for i, a in enumerate(items):
            prev = items[i - 1] if i > 0 else None
            nxt = items[i + 1] if i < len(items) - 1 else None
            d = f"{ROOT}/articles/{a['slug']}"
            os.makedirs(d, exist_ok=True)
            open(f"{d}/index.html", "w").write(build_article(a, prev, nxt))

    open(f"{ROOT}/articles/index.html", "w").write(build_index(groups))
    print(f"wrote {len(ARTS)} article pages + archive index")


if __name__ == "__main__":
    main()
