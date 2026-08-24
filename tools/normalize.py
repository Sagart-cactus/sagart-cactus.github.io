#!/usr/bin/env python3
"""Fix structural defects inherited from LinkedIn's markup.

1. <p> wrapping block elements (<p><ul>…</ul></p>) is invalid; browsers split it
   into a stray empty paragraph. Unwrap so blocks are siblings, keeping any
   inline lead-in text in its own paragraph.
2. A couple of lists LinkedIn flattened into run-on text.
"""

import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
from bs4 import BeautifulSoup, NavigableString, Tag

BLOCK = {"ul", "ol", "pre", "blockquote", "h2", "h3", "h4", "hr", "p"}


def unwrap_block_paragraphs(html):
    soup = BeautifulSoup(html, "html.parser")
    changed = True
    passes = 0
    while changed and passes < 5:
        changed = False
        passes += 1
        for p in soup.find_all("p"):
            if not any(isinstance(c, Tag) and c.name in BLOCK for c in p.children):
                continue
            new_nodes, buf = [], []

            def flush():
                if not buf:
                    return
                txt = "".join(str(x) for x in buf).strip()
                if txt:
                    np = BeautifulSoup(f"<p>{txt}</p>", "html.parser").p
                    new_nodes.append(np)
                buf.clear()

            for child in list(p.children):
                if isinstance(child, Tag) and child.name in BLOCK:
                    flush()
                    new_nodes.append(child.extract())
                else:
                    buf.append(child)
            flush()
            for node in reversed(new_nodes):
                p.insert_after(node)
            p.decompose()
            changed = True
    return str(soup)


FLATTENED = [
    # (slug, before, after)
    ("building-giant-sdks-apis-whats-next",
     "Adapters:Linux implementation (uses seccomp)macOS implementation "
     "(uses sandbox profile)Test mock (returns canned responses)",
     "Adapters: Linux implementation (uses seccomp), macOS implementation "
     "(uses sandbox profile), and a test mock (returns canned responses)"),
]


def main():
    arts = json.load(open(os.path.join(HERE, "articles.json")))
    fixed_flat = 0
    for a in arts:
        for slug, before, after in FLATTENED:
            if a["slug"] == slug and before in a["html"]:
                a["html"] = a["html"].replace(before, after)
                fixed_flat += 1
        a["html"] = unwrap_block_paragraphs(a["html"])

    json.dump(arts, open(os.path.join(HERE, "articles.json"), "w"), indent=1)

    remaining = sum(len(re.findall(r"<p>\s*<(?:ul|ol|pre|blockquote|h2|h3)", a["html"]))
                    for a in arts)
    empty_p = sum(len(re.findall(r"<p>\s*</p>", a["html"])) for a in arts)
    print(f"flattened lists fixed: {fixed_flat}")
    print(f"invalid <p><block> remaining: {remaining}")
    print(f"empty paragraphs remaining: {empty_p}")


if __name__ == "__main__":
    main()
