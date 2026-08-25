#!/usr/bin/env python3
"""Generate the on-site article archive from articles.json."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = "https://sagart-cactus.github.io"
ARTICLES_JSON = os.path.join(HERE, "articles.json")

with open(ARTICLES_JSON, encoding="utf-8") as _handle:
    ARTICLES = json.load(_handle)

FAVICON = ("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2064%2064'"
           "%3E%3Crect%20width='64'%20height='64'%20rx='14'%20fill='%239c3d17'/%3E%3Ctext%20x='32'%20y='44'%20"
           "font-family='Georgia,serif'%20font-size='34'%20font-weight='700'%20text-anchor='middle'%20"
           "fill='%23fcfcfa'%3EST%3C/text%3E%3C/svg%3E")

# Consolidated guide sites, each one a companion to an article group.
# "group" must match a group name in articles_source.json, or "" for none.
GUIDES = [
    {
        "name": "RAG · The Visual Field Guide",
        "url": "https://sagart-cactus.github.io/learn-rag/",
        "short": "RAG field guide",
        "group": "Agents, evaluation and retrieval",
        "blurb": "Why retrieval exists, how embeddings and BM25 actually work, chunking, "
                 "reranking and ANN indexes.",
    },
    {
        "name": "Managed Agents · The Visual Field Guide",
        "url": "https://sagart-cactus.github.io/learn-managed-agents/",
        "short": "Managed Agents field guide",
        "group": "Agents, evaluation and retrieval",
        "blurb": "Orchestration, parent and child isolation, parallelism, model matching, cost, "
                 "and when not to reach for an agent.",
    },
    {
        "name": "The MCP Knowledgebase",
        "url": "https://sagart-cactus.github.io/learn-mcp/",
        "short": "The MCP Knowledgebase",
        "group": "Model Context Protocol",
        "blurb": "Model Context Protocol explained: architecture, primitives, call flow, server "
                 "design and security.",
    },
    {
        "name": "Anatomy of an AI Coding Agent",
        "url": "https://sagart-cactus.github.io/learn-codex-internals/",
        "short": "Anatomy of an AI Coding Agent",
        "group": "Inside Codex CLI, an eight-part series",
        "blurb": "An eight-part dissection of the OpenAI Codex CLI: architecture, protocols, "
                 "prompt assembly, sandboxing, tools and safety.",
    },
    {
        "name": "Claude Code Plugins · The Definitive Visual Guide",
        "url": "https://sagart-cactus.github.io/learn-claude-code-plugin/",
        "short": "Claude Code Plugins guide",
        "group": "Agent tooling and team practice",
        "blurb": "Skills, agents, hooks, MCP and LSP servers, monitors, security and workflow "
                 "automation.",
    },
]

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
    return datetime.strptime(d, "%b %d, %Y").date().isoformat()  # noqa: DTZ007


def pretty(d):
    parsed = datetime.strptime(d, "%b %d, %Y").date()  # noqa: DTZ007
    return parsed.strftime("%-d %B %Y")


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


def html_voids(html):
    """BeautifulSoup round-trips void elements as XHTML (<br/>); HTML wants <br>."""
    return re.sub(r"<(br|hr|img)\s*/>", r"<\1>", html)


def build_article(a, prev, nxt):
    depth = 2
    up = "../" * depth
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
{html_voids(a['html'])}
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

    extra = (f'<meta property="article:published_time" content="{iso(a["date"])}">\n'
             f'<meta property="article:author" content="Sagar Trivedi">')

    return page(f"{a['title']} · Sagar Trivedi", a["excerpt"], canonical,
                body, depth, extra_head=extra, jsonld=jsonld)


def group_id(name):
    """Stable, readable anchor id. Must not use hash(): it is salted per process."""
    return "g-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def entry_row(a):
    """One article row in the archive listing."""
    return f"""          <li>
            <a class="entry" href="{a['slug']}/">
              <span class="entry-title">{escape(a['title'])}</span>
              <span class="entry-meta"><time datetime="{iso(a['date'])}">{pretty(a['date'])}</time>
                <span class="dot">·</span>{a['minutes']} min</span>
            </a>
            <p class="entry-excerpt">{escape(a['excerpt'])}…</p>
          </li>"""


def guides_section():
    items = "\n".join(
        f"""          <li>
            <a href="{g['url']}">{escape(g['name'])}</a>
            <span>{escape(g['blurb'])}</span>
          </li>"""
        for g in GUIDES
    )
    return f"""      <section class="group guides" aria-labelledby="g-visual-field-guides">
        <h2 id="g-visual-field-guides">Visual field guides</h2>
        <p class="group-note">Each series is consolidated into a single illustrated guide, built
        to be handed to a team rather than read once.</p>
        <ul class="guide-list">
{items}
        </ul>
      </section>"""


def companion_link(group_name):
    """Guides that consolidate a given article group."""
    matches = [g for g in GUIDES if g["group"] == group_name]
    if not matches:
        return ""
    anchors = [f'<a href="{g["url"]}">{escape(g["short"])}</a>' for g in matches]
    links = anchors[0] if len(anchors) == 1 else " and ".join(
        [", ".join(anchors[:-1]), anchors[-1]])
    label = "Companion guide" if len(matches) == 1 else "Companion guides"
    return f'\n        <p class="companion">{label}: {links}</p>'


def build_index(groups):
    parts = [guides_section()]
    for name, items in groups.items():
        rows = [entry_row(a) for a in items]
        parts.append(f"""      <section class="group" aria-labelledby="{group_id(name)}">
        <h2 id="{group_id(name)}">{escape(name)}</h2>{companion_link(name)}
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


def write_sitemap(groups):
    """Sitemap over every page, newest article first."""
    urls = [(f"{SITE}/", None), (f"{SITE}/articles/", None)]
    arts = sorted((a for v in groups.values() for a in v),
                  key=lambda a: iso(a["date"]), reverse=True)
    urls += [(f"{SITE}/articles/{a['slug']}/", iso(a["date"])) for a in arts]

    body = "\n".join(
        "  <url>\n    <loc>{}</loc>{}\n  </url>".format(
            loc, f"\n    <lastmod>{mod}</lastmod>" if mod else "")
        for loc, mod in urls)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f"{body}\n</urlset>\n")
    with open(f"{ROOT}/sitemap.xml", "w", encoding="utf-8") as handle:
        handle.write(xml)

    with open(f"{ROOT}/robots.txt", "w", encoding="utf-8") as handle:
        handle.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    return len(urls)


def main() -> int:
    groups = {}
    for a in ARTICLES:
        groups.setdefault(a["group"], []).append(a)

    os.makedirs(f"{ROOT}/articles", exist_ok=True)
    os.makedirs(f"{ROOT}/assets", exist_ok=True)

    # article pages, with prev/next inside each group
    for items in groups.values():
        for i, a in enumerate(items):
            prev = items[i - 1] if i > 0 else None
            nxt = items[i + 1] if i < len(items) - 1 else None
            directory = f"{ROOT}/articles/{a['slug']}"
            os.makedirs(directory, exist_ok=True)
            with open(f"{directory}/index.html", "w", encoding="utf-8") as handle:
                handle.write(build_article(a, prev, nxt))

    with open(f"{ROOT}/articles/index.html", "w", encoding="utf-8") as handle:
        handle.write(build_index(groups))
    n = write_sitemap(groups)
    print(f"wrote {len(ARTICLES)} article pages + archive index")
    print(f"wrote sitemap.xml ({n} urls) and robots.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
