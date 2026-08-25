#!/usr/bin/env python3
"""Fetch the LinkedIn articles listed in articles_source.json and extract clean HTML.

LinkedIn's markup is wrapped in layout divs and utility classes. This reduces each
article to a whitelist of semantic tags, repairs two structural defects in the
source (see `normalise`), and writes everything to articles.json for build_site.py.

Usage:  python tools/fetch_articles.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from html import escape

from bs4 import BeautifulSoup, NavigableString, Tag

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "articles_source.json")
OUTPUT = os.path.join(HERE, "articles.json")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
)
REQUEST_DELAY = 1.5
WORDS_PER_MINUTE = 220

# Tags kept in the output. Everything else is unwrapped, keeping its text.
ALLOWED = {
    "p", "h2", "h3", "h4", "ul", "ol", "li", "pre", "code",
    "blockquote", "hr", "a", "strong", "em", "br",
}
RENAME = {"b": "strong", "i": "em"}
DROPPED = {"figure", "img", "svg", "button", "icon"}
# Block tags that must never be nested inside a <p>.
BLOCK = {"ul", "ol", "pre", "blockquote", "h2", "h3", "h4", "hr", "p"}

# Lists that LinkedIn flattened into run-on text in the published original.
FLATTENED_LISTS = {
    "part-7-safety-net": [
        ("three things happens:The policy", "three things happens: The policy"),
        ("pre-approved it.The policy", "pre-approved it. The policy"),
        ("explicit yes.The policy", "explicit yes. The policy"),
    ],
    "building-giant-sdks-apis-whats-next": [
        (
            (
                "Adapters:Linux implementation (uses seccomp)macOS implementation "
                "(uses sandbox profile)Test mock (returns canned responses)"
            ),
            (
                "Adapters: Linux implementation (uses seccomp), macOS implementation "
                "(uses sandbox profile), and a test mock (returns canned responses)"
            ),
        ),
    ],
}


def slug_from_url(url: str) -> str:
    """LinkedIn slugs carry an author and id suffix; strip it for clean paths."""
    slug = url.rstrip("/").split("/")[-1]
    return re.sub(r"-(?:sagar-)?trivedi-[a-z0-9]+$", "", slug)


def serialize(node) -> str:
    """Render a node down to whitelisted tags, dropping attributes except href."""
    if isinstance(node, NavigableString):
        return escape(str(node))
    if not isinstance(node, Tag):
        return ""

    name = node.name.lower()
    if name == "pre":
        return f"<pre><code>{escape(node.get_text().rstrip())}</code></pre>"
    if name in ("br", "hr"):
        return f"<{name}>"
    if name in DROPPED:
        return ""

    inner = "".join(serialize(child) for child in node.children)

    if name == "a":
        href = node.get("href", "")
        if not href.startswith(("http://", "https://")):
            return inner
        return f'<a href="{escape(href)}" rel="nofollow">{inner}</a>'

    name = RENAME.get(name, name)
    return f"<{name}>{inner}</{name}>" if name in ALLOWED else inner


def collapse_whitespace(html: str) -> str:
    """Collapse LinkedIn's source indentation, leaving <pre> contents untouched."""
    parts: list[str] = []
    cursor = 0
    for match in re.finditer(r"<pre><code>.*?</code></pre>", html, re.DOTALL):
        parts.append(re.sub(r"\s+", " ", html[cursor:match.start()]))
        parts.append(match.group(0))
        cursor = match.end()
    parts.append(re.sub(r"\s+", " ", html[cursor:]))
    return re.sub(r">\s+<", "><", "".join(parts)).strip()


def unwrap_block_paragraphs(html: str) -> str:
    """Split <p> elements that wrap block content.

    LinkedIn emits `<p><ul>…</ul></p>`, which is invalid. Browsers recover by
    closing the paragraph early and leaving a stray empty one behind, so do the
    split deliberately: inline lead-in text keeps its own <p>, blocks become
    siblings.
    """
    soup = BeautifulSoup(html, "html.parser")

    for _ in range(5):                     # nesting is shallow; bound the passes
        targets = [
            p for p in soup.find_all("p")
            if any(isinstance(c, Tag) and c.name in BLOCK for c in p.children)
        ]
        if not targets:
            break
        for para in targets:
            _split_paragraph(para)

    return str(soup)


def _split_paragraph(para: Tag) -> None:
    replacements: list[Tag] = []
    inline: list = []

    def flush(buffer: list) -> None:
        text = "".join(str(node) for node in buffer).strip()
        if text:
            replacements.append(BeautifulSoup(f"<p>{text}</p>", "html.parser").p)
        buffer.clear()

    for child in list(para.children):
        if isinstance(child, Tag) and child.name in BLOCK:
            flush(inline)
            replacements.append(child.extract())
        else:
            inline.append(child)
    flush(inline)

    for node in reversed(replacements):
        para.insert_after(node)
    para.decompose()


def normalise(html: str, slug: str) -> str:
    for before, after in FLATTENED_LISTS.get(slug, []):
        html = html.replace(before, after)
    return unwrap_block_paragraphs(html)


def extract(page_html: str, url: str) -> dict | None:
    soup = BeautifulSoup(page_html, "html.parser")
    article = soup.find("article")
    if article is None:
        return None

    header = article.find("header")
    date_match = re.search(
        r"Published\s+([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})",
        header.get_text(" ", strip=True) if header else "",
    )

    # The body is the largest direct child <div>; siblings are cover art and chrome.
    divs = article.find_all("div", recursive=False)
    if not divs:
        return None
    body = max(divs, key=lambda d: len(d.get_text()))

    blocks: list[str] = []
    for child in body.find_all(recursive=False):
        if child.name == "hr":
            blocks.append("<hr>")
            continue
        element = child.find(recursive=False) or child
        if element.name in ("figure", "img"):
            continue
        fragment = collapse_whitespace(serialize(element))
        if not fragment or fragment in ("<p></p>", "<p> </p>"):
            continue
        # LinkedIn uses <h3> for top-level sections; our page title is the <h1>.
        fragment = re.sub(r"^<h3>", "<h2>", fragment)
        fragment = re.sub(r"</h3>$", "</h2>", fragment)
        blocks.append(fragment)

    slug = slug_from_url(url)
    html = normalise("\n".join(blocks), slug)
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    words = len(text.split())
    title = article.find("h1")

    return {
        "title": title.get_text(strip=True) if title else None,
        "date": date_match.group(1) if date_match else None,
        "source_url": url,
        "slug": slug,
        "html": html,
        "words": words,
        "minutes": max(1, round(words / WORDS_PER_MINUTE)),
        "excerpt": re.sub(r"\s+", " ", text)[:200].strip(),
    }


def download(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read().decode("utf-8", "replace")


def main() -> int:
    with open(SOURCE, encoding="utf-8") as handle:
        groups: dict[str, list[list[str]]] = json.load(handle)

    articles = []
    expected = sum(len(items) for items in groups.values())

    for group, items in groups.items():
        for listed_title, url in items:
            try:
                page_html = download(url)
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                print(f"FAIL     {url}  ({error})", file=sys.stderr)
                continue

            article = extract(page_html, url)
            if article is None:
                print(f"NOPARSE  {url}", file=sys.stderr)
                continue

            article["group"] = group
            article["listed_title"] = listed_title
            articles.append(article)
            print(f"ok  {article['words']:>6} words  "
                  f"{article['minutes']:>2} min  {article['slug']}")
            time.sleep(REQUEST_DELAY)

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(articles, handle, indent=1)

    print(f"\nextracted {len(articles)} / {expected} articles")
    return 0 if len(articles) == expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
