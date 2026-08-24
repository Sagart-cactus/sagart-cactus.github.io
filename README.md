# Personal resume site

**Published at <https://sagart-cactus.github.io/>**

A single static page, positioned for the OpenAI **Applied AI Architect** role (Technical Success,
Delhi / Mumbai / Bangalore). No build step, no framework, no dependencies beyond one Google Fonts
stylesheet (IBM Plex Sans + IBM Plex Mono). It opens correctly from `file://` and deploys by
dropping the file onto any static host.

```
index.html    the entire site: markup, styles, print styles, theme toggle, JSON-LD
README.md     this file
```

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

## GitHub Pages

Already live. Because the repository is named `sagart-cactus.github.io`, it is a GitHub user site:
Pages enabled itself on first push and serves from `main` at the root path, with HTTPS enforced.
There was no Settings step.

To publish a change, just push:

```bash
git add index.html && git commit -m "Update resume" && git push
```

The rebuild takes about half a minute. To check whether it has finished:

```bash
gh api repos/Sagart-cactus/sagart-cactus.github.io/pages --jq .status
```

For a custom domain later, add it under **Settings → Pages → Custom domain**, commit the `CNAME`
file Pages creates, and point a `CNAME` DNS record at `sagart-cactus.github.io`. Leave **Enforce
HTTPS** on, and update the canonical link, `og:url` and JSON-LD `url` in `index.html` to match.

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

Everything else is done. The site URL is set to `https://sagart-cactus.github.io/` in all three
places (canonical link, `og:url`, JSON-LD `url`). All five open-source links were checked against
the live repositories and return 200; note that the OptiPod repo is lowercase `optipod`, and the
link uses that. Dates, titles, education, certification and the article list are filled in from your
resume and LinkedIn.

## One thing to reconcile

Your resume says the model change moved hallucination **from 18% to 13%**, which is a 27.8% relative
reduction. Your brief for this site said **roughly 35% relative**. Those do not describe the same
number. The page currently uses "roughly 35% relative", since that was your wording for the site,
and it keeps the absolute production error rate off a public page. Worth settling before an
interviewer does the arithmetic. The same bullet also claims a 27% verbosity cut, which is
suspiciously close to 27.8%, so the two figures may have been crossed somewhere.

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
