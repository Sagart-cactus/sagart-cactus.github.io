# Personal resume site

**Published at <https://sagartrivedi.dev/>**

A single static page, positioned for the OpenAI **Applied AI Architect** role (Technical Success,
Delhi / Mumbai / Bangalore). No build step, no framework, no dependencies beyond one Google Fonts
stylesheet (IBM Plex Sans + IBM Plex Mono). It opens correctly from `file://` and deploys by
dropping the file onto any static host.

```
index.html          the resume page: markup, styles, print styles, theme toggle, JSON-LD
articles/           25 republished articles, one directory per article
articles/index.html the writing archive
assets/site.css     shared styles for the archive and article pages
tools/              the scripts that fetch and rebuild the archive
sitemap.xml         generated; every page, articles newest first
robots.txt          generated; points crawlers at the sitemap
ruff.toml           lint config for tools/
README.md           this file
```

`sitemap.xml` and `robots.txt` are build output. Edit `tools/build_site.py`, not those files.

The resume page keeps all of its CSS inline and depends on nothing, exactly as before. Only the
article pages use the shared stylesheet, because inlining 400 lines of CSS into 26 pages would be
worse. Every path is relative, so the whole site still opens correctly from `file://`.

## Print / PDF

The print styles live in an `@media print` block inside `index.html` rather than a separate
`print.css`. That keeps the page genuinely self-contained, a single file that behaves identically
from `file://`, from a host, and when a recruiter hits Cmd-P. Printing gives a clean single-column
document: the theme toggle is dropped, colours flatten to black on white, project and footer link
destinations are printed in parentheses, and headings stay with the content that follows them.

Verified with headless Chrome: it renders to five pages with no orphaned headings and no
half-empty pages. If you want it shorter, the Writing section is the obvious thing to trim; it
accounts for roughly a page and a half.

To check it yourself:

```bash
open index.html
```

Then print to PDF with background graphics off.

If you would rather have the print rules in their own file, cut the `@media print { … }` block into
`print.css` and link it with `<link rel="stylesheet" href="print.css" media="print">`. The page will
still work from `file://`, but you then have two files to keep in sync.

## Local preview

Just open the file, or serve it if you prefer a real origin:

```bash
python3 -m http.server 8000
```

## GitHub Pages and the custom domain

Live at **<https://sagartrivedi.dev/>**. The repository is named `sagart-cactus.github.io`, which
makes it a GitHub *user site*: Pages enabled itself on first push and serves from `main` at the root
path.

The custom domain is set on the repo (`CNAME` file at the root, committed by GitHub), with HTTPS
enforced and a Let's Encrypt certificate. DNS lives at Namecheap: four `A` records and four `AAAA`
records on the apex pointing at GitHub Pages, plus a `CNAME` on `www`. `sagart-cactus.github.io`
now 301-redirects to the custom domain, and so do the five `learn-*` guide sites, which moved to
`sagartrivedi.dev/learn-*/` automatically because they hang off the user site.

Two things to know about `.dev`: it is on the HSTS preload list, so browsers refuse plain HTTP at
the TLD level. If the certificate is ever missing or expired the site fails outright rather than
showing a warning. And domain *verification* (account Settings, a `_github-pages-challenge-*` TXT
record) is a separate step from setting the *custom domain* on the repo; doing only the first leaves
the domain serving 404s.

To publish a change, just push:

```bash
git add index.html && git commit -m "Update resume" && git push
```

The rebuild takes about half a minute. To check whether it has finished:

```bash
gh api repos/Sagart-cactus/sagart-cactus.github.io/pages --jq .status
```

If the domain ever changes again, update `SITE` in `tools/build_site.py`, the canonical link,
`og:url` and JSON-LD `url` in `index.html`, and the five guide URLs in `GUIDES`, then rebuild. The
old host is listed in `LEGACY_HOSTS` so links inside archived articles get rewritten automatically.

## Deploying to Vercel

Vercel treats a repository with a bare `index.html` as a static site, so leave the framework preset as
*Other* and leave the build and output settings empty.

Via the dashboard: **Add New → Project**, import the repository, accept the defaults, deploy.

Via the CLI:

```bash
npx vercel --prod
```

Answer *no* when it asks whether to override the build settings. Add a custom domain under
**Project → Settings → Domains**; Vercel issues the certificate itself.

## Fill these in before publishing

Run `grep -n PLACEHOLDER index.html` to list them in place.

1. **Email address.** A commented-out `<li>` in the contact list holds a `you@example.com`
   placeholder. Fill in your address and uncomment it to publish, then do the same for the
   commented footer link and add an `"email"` field to the JSON-LD block. Two things to know: HTML
   comments are served in the public page source, so a real address parked in a commented-out block
   is still scrapeable, and publishing an address on a public page invites spam either way. Decide
   deliberately rather than leaving it half-done.
2. **Last updated.** The footer says "August 2026" in both the visible text and the `datetime`
   attribute. Worth changing whenever you edit the page.
3. **Open Graph image** *(optional)*. Two commented meta tags. Without one, link previews show a
   text-only card. If you add a 1200×630 PNG, also switch `twitter:card` from `summary` to
   `summary_large_image`.
4. **Twitter handle** *(optional)*. A commented `twitter:site` tag; delete it if you do not want one.

Everything else is done. The site URL is set to `https://sagartrivedi.dev/` in all three
places (canonical link, `og:url`, JSON-LD `url`). All five open-source links were checked against
the live repositories and return 200; note that the OptiPod repo is lowercase `optipod`, and the
link uses that. Dates, titles, education, certification and the article list are filled in from your
resume and LinkedIn.

## Note on the hallucination figure

Settled: the measured change is **18% to 13%**, a 27.8% relative reduction. The page says "roughly
28% relative", which keeps the absolute production error rates off a public page while stating a
number that survives arithmetic. An earlier draft said "roughly 35% relative"; that was wrong and
has been corrected. If you quote this result anywhere else, 28% relative (or the raw 18% to 13%) is
the defensible form.

## What was tailored for this role, and what was held back

Aligned to the posting, which asks for a senior technical owner who takes enterprise customers from
evaluation through production adoption:

- Headline is now **Applied AI Architect · Enterprise AI Adoption**, and the location line reads
  "Bangkok, Thailand · Indian citizen", which answers the India-based role's first filter without
  reading as a relocation plea.
- The summary leads with being the technical counterpart to stakeholders, and names the arc the
  posting cares about: discovery, use-case selection, architecture across models, data, integration,
  security and governance, then evaluation and telemetry.
- Experience is restructured employer-first with the full title progression, so fourteen years of
  history reads at a glance.
- Skills gained an **Architecture** cluster (APIs, distributed systems, data integration, identity,
  security, privacy) and a **Working with customers** cluster, both lifted almost directly from the
  posting's qualifications.
- SprintFoundry's description now mentions the OpenAI Codex runtime, and the Codex CLI article
  series is grouped as its own block.

Deliberately kept off the page, per your original rules. All of these are in the resume PDF but not
here: absolute request volumes, the number of agents served, dollar figures for cloud savings, every
team headcount, the third-party chat vendor's product name, and your phone number. Internal
architecture is described by shape ("streaming ingestion, warehousing, retrieval over customer and
knowledge context") rather than by naming the stack as a blueprint. Percentages, ratios and
percentiles were kept, since your rule allows them: 94–97% judge precision, 98.5% cache hit rate,
99.965% uptime, 27% verbosity reduction, roughly 7× cost reduction.

The experience heading is now just **Honest**, with no descriptor after it. Note that the summary
paragraph and the meta description still say "a regulated digital bank" as a generic descriptor of
the sector. That reads naturally in prose and matches your original brief, but if you want the
phrase gone from the page entirely, those are the two remaining spots. FinOps results are described
as "cutting annual cloud spend substantially" rather than with the dollar figure.

## The writing archive

All 25 LinkedIn articles are republished at `/articles/`, grouped the same way as the resume's
Writing section. Each article gets its own page with a publish date, reading time, prev/next links
within its group, `BlogPosting` structured data, and a link back to the LinkedIn original.

**Canonical.** Each article page points its canonical at itself, claiming your domain as the home of
your writing. LinkedIn is a much stronger domain and will likely outrank you for a while; that is
expected and it resolves as the site accumulates its own history. If you ever want to reverse this,
change the `<link rel="canonical">` in the generated pages to `a["source_url"]` in
`tools/build_site.py` and rebuild.

**Diagrams are self-hosted.** Each article carries explainer diagrams; there are 48 in total across
the 25 articles. LinkedIn serves them as GIF, and the 21 animated ones weigh about 23 MB between
them. `tools/fetch_media.py` downloads everything, re-encodes animated GIFs to H.264 MP4, and
extracts a poster frame. The whole set drops from **25.3 MB to 3.6 MB**; the worst single file goes
from 2674 KB to 46 KB. Animated diagrams render as `<video autoplay loop muted playsinline>`, which
behaves like a GIF but is roughly two orders of magnitude smaller. Median article page weight,
including media, is 89 KB.

Article cover images are still skipped: they are decorative, and the URLs are signed CDN links that
rot.

**Reduced motion is respected.** A visitor with `prefers-reduced-motion: reduce` gets paused videos
with controls rather than autoplay. CSS cannot pause a video, so this is done in JS.

**Alt text is generated**, not authored: each diagram gets `Diagram: <nearest preceding heading>`,
because LinkedIn's own alt text is the useless string "Article content" on all 48. It is a large
improvement over that, but it is not a substitute for a human describing what each diagram shows.
Worth a pass if you want these to work properly in screen readers and image search.

### Visual field guides

Five separate repositories publish consolidated, illustrated versions of the article series. They
are GitHub Pages project sites, so they already live on this same domain under `/learn-*/`:

| Guide | Consolidates |
| --- | --- |
| [RAG](https://sagartrivedi.dev/learn-rag/) | Agents, evaluation and retrieval |
| [Managed Agents](https://sagartrivedi.dev/learn-managed-agents/) | Agents, evaluation and retrieval |
| [The MCP Knowledgebase](https://sagartrivedi.dev/learn-mcp/) | Model Context Protocol |
| [Anatomy of an AI Coding Agent](https://sagartrivedi.dev/learn-codex-internals/) | Inside Codex CLI |
| [Claude Code Plugins](https://sagartrivedi.dev/learn-claude-code-plugin/) | Agent tooling and team practice |

They are linked in two places: a "Visual field guides" block at the top of both the resume's Writing
section and the archive index, and a per-group "Companion guide" line on the archive so a reader
inside one series finds its guide without scrolling back up.

The list lives in the `GUIDES` constant in `tools/build_site.py`. Each entry has a `name`, `url`,
`short` label used in the companion lines, a `blurb`, and a `group` that must match a group name in
`articles_source.json` (use `""` for a guide with no matching group). The archive block is generated
from it; **the copy in `index.html` is hand-written, so update both** if you add a guide.

### Rebuilding or adding an article

The pipeline needs `beautifulsoup4`. Use a virtualenv, since macOS system Python refuses installs:

```bash
python3 -m venv .venv && .venv/bin/pip install beautifulsoup4
```

To add newly published articles, add them to the right group in `tools/articles_source.json`, then:

```bash
.venv/bin/python tools/fetch_articles.py \
  && .venv/bin/python tools/fetch_media.py \
  && .venv/bin/python tools/build_site.py
```

`fetch_articles.py` pulls each article, strips LinkedIn's markup down to a whitelist of semantic
tags, and repairs the structural defects described below. `fetch_media.py` downloads the diagrams
and re-encodes the animated ones (needs `ffmpeg` on PATH). `build_site.py` writes the article pages,
the archive index, `sitemap.xml` and `robots.txt`.

Both scripts are deterministic: rebuilding without changing `articles.json` produces byte-identical
output, so a rebuild never shows up as noise in `git diff`. The Writing links in `index.html` are
not regenerated, so add new entries there by hand.

### What was repaired during import

LinkedIn's exported markup had two defects worth knowing about, both fixed:

- **126 invalid `<p>` wrappers** across 19 articles, where a list or code block sat inside a
  paragraph. Browsers silently split these, leaving stray empty paragraphs. `normalize.py` unwraps
  them so blocks are proper siblings.
- **Two flattened lists**, in *Part 7: The Safety Net* and *Building on the Giant*, where items ran
  together without spaces (`happens:The policy says…`). These are defects in the LinkedIn originals,
  not artifacts of the import, and they still read that way on LinkedIn. The on-site copies are
  fixed. Worth correcting at the source if you edit those articles.
- **A "Recommended by LinkedIn" heading** that LinkedIn injects into the middle of the body, which
  had leaked into 19 of the 25 articles. Now stripped.
- **Dropped paragraphs.** An earlier version of the extractor skipped `<figure>` blocks wholesale,
  which also discarded text that sat alongside the diagrams. Handling images properly recovered it,
  including two full sentences in *Stop re-explaining your stack*.
- **Cross-references now stay on-site.** Where an article links to another of your articles, the
  link points at the local copy instead of back to LinkedIn, and `rel="nofollow"` is dropped since
  the link is no longer outbound.

## Code quality

Checks this repo is expected to pass, and did at last commit:

- **HTML validity.** All 27 pages pass the W3C Nu validator with zero errors and zero warnings.
  Two defects were fixed to get there: the favicon data URI contained unencoded spaces (invalid on
  every page, including the resume), and BeautifulSoup was round-tripping void elements as XHTML
  (`<br/>`) in 15 article pages.
- **Accessibility.** Every page has one `<h1>`, no skipped heading levels, a skip link whose target
  exists, `header`/`main`/`footer` landmarks, labelled `<nav>` elements, accessible names on all
  buttons, `aria-hidden` on decorative SVGs, and a visible focus ring. Text and accent colours clear
  WCAG AA in both themes.
- **Deterministic builds.** Rebuilding produces byte-identical output. The group anchor ids were
  originally derived from Python's `hash()`, which is salted per process, so every rebuild churned
  the ids; they are now readable slugs like `#g-model-context-protocol` that also work as deep links.
- **Lint.** `ruff check .` passes clean against `E,F,W,B,SIM,PERF,UP,I,C4,ISC,DTZ`.

To re-run the checks:

```bash
.venv/bin/pip install ruff && .venv/bin/ruff check .
```

For HTML, POST a page to the validator:

```bash
curl -s -H "Content-Type: text/html; charset=utf-8" --data-binary @index.html "https://validator.w3.org/nu/?out=json"
```

### Known trade-off

The design tokens are defined twice: inline in `index.html` and again in `assets/site.css`. That is
deliberate, because the resume page is required to be a single self-contained file, and inlining the
full stylesheet into 26 article pages would be worse. The two sets are currently identical. If you
change a colour in one, change it in the other, or the resume and the archive will drift apart.

## House style

No em dashes anywhere in `index.html`. Where one would normally go, the text uses a colon, a comma,
or a restructured sentence. En dashes are still used, but only for ranges: date spans
("Mar 2024 – Present"), numeric ranges ("94–97%"), and the official AWS certification name. If you
edit the page later, `grep '—' index.html` should always return nothing.

## Notes on what is in the page

- **Themes.** Follows `prefers-color-scheme` by default. The toggle writes a `theme` key to
  `localStorage` and sets `data-theme` on `<html>`; an inline script in `<head>` applies it before
  first paint so there is no flash. Everything is wrapped in `try/catch` because some browsers block
  `localStorage` on `file://`.
- **Accessibility.** Semantic landmarks, one `<h1>` with no skipped heading levels (verified), a
  skip link, a visible focus ring on every interactive element, and text/accent colours that clear
  WCAG AA in both themes. No horizontal overflow at 375px.
