#!/usr/bin/env python3
"""Fetch Sagar's LinkedIn articles and extract clean, self-hosted HTML."""

import json, os, re, time, sys, urllib.request
from html import escape
from bs4 import BeautifulSoup, NavigableString, Tag

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

# group -> [(title, url)]
HERE = os.path.dirname(os.path.abspath(__file__))
GROUPS = json.load(open(os.path.join(HERE, "articles_source.json")))

ALLOWED = {"p", "h2", "h3", "h4", "ul", "ol", "li", "pre", "code",
           "blockquote", "hr", "a", "strong", "em", "br"}
RENAME = {"b": "strong", "i": "em"}


def slug_from_url(url):
    s = url.rstrip("/").split("/")[-1]
    # strip trailing "-sagar-trivedi-<id>" (or "-trivedi-<id>")
    s = re.sub(r"-sagar-trivedi-[a-z0-9]+$", "", s)
    s = re.sub(r"-trivedi-[a-z0-9]+$", "", s)
    return s


def serialize(node):
    if isinstance(node, NavigableString):
        return escape(str(node))
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()

    if name == "pre":
        return "<pre><code>" + escape(node.get_text().rstrip()) + "</code></pre>"
    if name == "br":
        return "<br>"
    if name == "hr":
        return "<hr>"
    if name in ("figure", "img", "svg", "button", "icon"):
        return ""

    inner = "".join(serialize(c) for c in node.children)

    if name == "a":
        href = node.get("href", "")
        if not href.startswith(("http://", "https://")):
            return inner
        return f'<a href="{escape(href)}" rel="nofollow">{inner}</a>'

    name = RENAME.get(name, name)
    if name not in ALLOWED:
        return inner            # unwrap, keep the text
    return f"<{name}>{inner}</{name}>"


def collapse_ws(html):
    # LinkedIn indents its markup; collapse runs of whitespace outside <pre>.
    out, i = [], 0
    for m in re.finditer(r"<pre><code>.*?</code></pre>", html, re.S):
        chunk = html[i:m.start()]
        out.append(re.sub(r"\s+", " ", chunk))
        out.append(m.group(0))
        i = m.end()
    out.append(re.sub(r"\s+", " ", html[i:]))
    s = "".join(out)
    s = re.sub(r">\s+<", "><", s)
    return s.strip()


def extract(html, url):
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article")
    if not article:
        return None

    header = article.find("header")
    date = None
    if header:
        m = re.search(r"Published\s+([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})",
                      header.get_text(" ", strip=True))
        if m:
            date = m.group(1)

    h1 = article.find("h1")
    title = h1.get_text(strip=True) if h1 else None

    # body = largest direct child <div>
    divs = [c for c in article.find_all("div", recursive=False)]
    if not divs:
        return None
    body = max(divs, key=lambda d: len(d.get_text()))

    parts = []
    for child in body.find_all(recursive=False):
        if child.name == "hr":
            parts.append("<hr>")
            continue
        el = child.find(recursive=False) or child
        if el.name in ("figure", "img"):
            continue
        frag = collapse_ws(serialize(el))
        if frag and frag not in ("<p></p>", "<p> </p>"):
            # LinkedIn uses h3 for top-level sections; article title is our h1.
            frag = re.sub(r"^<h3>", "<h2>", frag)
            frag = re.sub(r"</h3>$", "</h2>", frag)
            parts.append(frag)

    text = BeautifulSoup("\n".join(parts), "html.parser").get_text(" ", strip=True)
    words = len(text.split())

    return {
        "title": title,
        "date": date,
        "source_url": url,
        "slug": slug_from_url(url),
        "html": "\n".join(parts),
        "words": words,
        "minutes": max(1, round(words / 220)),
        "excerpt": re.sub(r"\s+", " ", text)[:200].strip(),
    }


def main():
    results = []
    for group, items in GROUPS.items():
        for title, url in items:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=45) as r:
                    raw = r.read().decode("utf-8", "replace")
            except Exception as e:
                print(f"FAIL  {url}  {e}", file=sys.stderr)
                continue
            art = extract(raw, url)
            if not art:
                print(f"NOPARSE  {url}", file=sys.stderr)
                continue
            art["group"] = group
            art["listed_title"] = title
            results.append(art)
            print(f"ok  {art['words']:>6} words  {art['minutes']:>2} min  {art['slug']}")
            time.sleep(1.5)

    json.dump(results, open(os.path.join(HERE, "articles.json"), "w"), indent=1)
    print(f"\nextracted {len(results)} / "
          f"{sum(len(v) for v in GROUPS.values())} articles")


if __name__ == "__main__":
    main()
