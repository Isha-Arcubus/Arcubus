# Arcubus Advisors website — operating guide

Everything you need to deploy this site and keep it updated: publishing articles, editing the
team section, wiring up Zoho, and the rules that keep it visible to Google and to AI assistants.

No build step. No framework. Every page is a plain HTML file you can open, read and edit.

---

## 1. What is in the folder

```
site/                                  ← this is what gets deployed
  index.html                           Home
  services.html                        Four service lines
  who-we-serve.html                    Consulting firms vs in-house tax teams
  process.html                         Ten-step benchmarking process
  knowledge-centre.html                Article index  ← add a card here for each new article
  knowledge/
    _TEMPLATE-article.html             COPY THIS to write a new article. Never edit in place.
                                       (blocked in robots.txt so the "REPLACE" text is never indexed)
    rejection-matrix-transfer-pricing-benchmarking.html
    benchmarking-intragroup-loans-oecd-chapter-x.html
    white-label-transfer-pricing-documentation.html
  glossary.html                        Definitions hub (targets "what is TNMM" style queries)
  in-house-vs-outsourced-transfer-pricing.html   Comparison page
  case-studies.html                    Anonymised engagements
  our-people.html                      Team  ← edit here
  contact.html                         Zoho enquiry form + Zoho Bookings embed
  thank-you.html                       Where the Zoho form returns after submit (noindex — deliberate)
  404.html                             Served automatically by Vercel
  robots.txt                           Crawler permissions (search + AI)
  sitemap.xml                          ← add a line for each new page
  llms.txt                             Curated summary for AI assistants ← add a line per article
  llms-full.txt                        Full plain text of the site, for retrieval
  vercel.json                          Headers, caching, redirects
  assets/
    site.css                           All styling. Design-system tokens + component classes.
    site.js                            Mobile nav toggle. The only script on the site.
    tokens/                            Design-system tokens — do not edit
    icons/                             13 brand line icons
    arcubus-logo.png, arcubus-mark.png, og-arcubus.png
UPDATING-THE-WEBSITE.md                This file
```

**Rules of the road**

- Never edit anything in `assets/tokens/` — those are the brand's colours, type and spacing.
- Never add a second stylesheet or a JS framework. Speed and crawlability are the whole point.
- The nav and footer are repeated in every page (that is deliberate — no JS means crawlers and
  AI see the full page). If you add a page to the nav, add it to **every** file. See §7.

---

## 2. Deploying to Vercel (first time, ~5 minutes)

1. Put the project in a Git repository (GitHub, GitLab or Bitbucket). The repo can contain this
   guide and the `site/` folder — that is fine.
2. In Vercel: **Add New → Project → Import** your repository.
3. On the configure screen:
   - **Framework Preset:** `Other`
   - **Root Directory:** `site`  ← important, this is the one setting that matters
   - **Build Command:** leave empty
   - **Output Directory:** leave empty
4. Click **Deploy**. You get a `*.vercel.app` URL in under a minute.
5. **Domain:** Project → Settings → Domains → add `arcubus.in` and `www.arcubus.in`. Vercel shows
   the DNS records to create at your registrar (an `A` record for the apex, a `CNAME` for `www`).
   Keep `arcubus.in` as the primary and let `www` redirect to it — the canonical tags in the HTML
   already point at `https://arcubus.in`.
6. After the domain is live, submit the sitemap once in
   [Google Search Console](https://search.google.com/search-console) and
   [Bing Webmaster Tools](https://www.bing.com/webmasters): `https://arcubus.in/sitemap.xml`.
   Bing's index is what Copilot and several AI assistants read from, so do not skip it.

**Every later update** is just: edit the file → commit → push. Vercel redeploys automatically,
usually in 20–40 seconds. Every push also gets its own preview URL, so you can check an article
before it goes to the live domain.

---

## 3. Publishing a new knowledge centre article

Nine steps. Steps 1–7 are the article; steps 8–9 are what makes it findable. Do not skip 8 and 9.

### Step 1 — Copy the template

Copy `site/knowledge/_TEMPLATE-article.html` to `site/knowledge/<your-slug>.html`.

Slug rules: lowercase, hyphens, no dates, no stop words, and it should read like the search query
you want to win — `benchmarking-management-service-charges`, not `article-7-final-v2`.

### Step 2 — Head of the file

Search for `REPLACE` and work top to bottom. In `<head>`:

| Field | What to write |
| --- | --- |
| `<title>` | Article title, then ` \| Arcubus Advisors`. Aim 55–62 characters before the pipe. |
| `<meta name="description">` | 150–160 characters that *answer* the question, not tease it. |
| `<link rel="canonical">` | `https://arcubus.in/knowledge/<your-slug>.html` |
| `og:url` | The same URL. |
| `og:title`, `og:description` | Same as title and description. |

### Step 3 — The JSON-LD block

Still in `<head>`, inside `<script type="application/ld+json">`. Replace, in the `Article` object:

- `headline` — the article title
- `description` — the meta description
- `datePublished` and `dateModified` — `YYYY-MM-DD`
- `mainEntityOfPage` — the full URL
- `articleSection` — the category (Benchmarking, Financial transactions, Documentation,
  White-label delivery, Advisory)
- `about` — keep `"Transfer pricing"` and add the specific topic

Also update the last item in the `BreadcrumbList` (`name` and `item`).

**To credit a person instead of the firm**, replace the `author` object with:

```json
"author": { "@type": "Person", "name": "Full Name", "jobTitle": "Director", "worksFor": { "@id": "https://arcubus.in/#organization" } }
```

and change the byline in the body to the same name. Do both or neither — a mismatch costs you
the rich result.

### Step 4 — Body of the article

In order down the page:

1. **Breadcrumb** — set the category name (two places on the line).
2. **Eyebrow** — the category.
3. **`<h1>`** — sentence case, ends in a full stop. House style, applies everywhere.
4. **Lede** — one or two sentences on what the reader will be able to do afterwards.
5. **Byline** — author, date (`18 June 2026` style), read time.

### Step 5 — Key takeaways box

Three to five bullets, each a complete sentence that stands alone out of context. **This box is
the single highest-leverage thing you write** — it is what an AI assistant lifts when it answers a
question with your page. Put the actual answer in bullet one. No teasers.

### Step 6 — The body copy

Inside `<div class="prose">`. Available markup:

```html
<h2>Section heading in sentence case.</h2>
<h3>Sub-heading.</h3>
<p>Body paragraph.</p>
<ul><li><strong>Lead-in</strong> — the point.</li></ul>
<blockquote>A pulled-out sentence.</blockquote>
<div class="tablescroll"><table class="plain">
  <thead><tr><th>Column</th><th>Column</th></tr></thead>
  <tbody><tr><td>Row label</td><td>Value</td></tr></tbody>
</table></div>
```

That is the whole vocabulary. Do not add inline colours, font sizes or custom classes — the
stylesheet already matches the brand, and one-off styling is how a site starts to look untidy.

Voice, briefly: sober and specific. Claims are verifiable ("within 1 working day"), never
superlative. Em dash for the turn in a sentence. Technical terms used without apology. No emoji,
ever. Where a fact is missing, put it in `[square brackets]` in plain sight rather than padding.

### Step 7 — FAQ block

Two to four questions, phrased **exactly as a client says them out loud** ("Can we just use the
parent's borrowing rate?"). Answer directly in the first sentence, then qualify.

Then copy each question and answer into the `FAQPage` block in the `<head>`. The JSON text must
match the visible text — Google checks, and a mismatch loses the FAQ rich result. Strip any HTML
tags from the JSON version.

### Step 8 — List it on the knowledge centre

Open `site/knowledge-centre.html`, find `<div class="grid g3">`, and paste a card as the **first**
child (newest first):

```html
<a class="articlecard" href="knowledge/your-slug.html"><span class="tag">Category</span><h3>Article title</h3><p>One-sentence summary — reuse the meta description.</p><span class="date">18 June 2026 · 7 min read</span></a>
```

### Step 9 — Tell the machines

**`site/sitemap.xml`** — add before `</urlset>`:

```xml
  <url>
    <loc>https://arcubus.in/knowledge/your-slug.html</loc>
    <lastmod>2026-08-14</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.7</priority>
  </url>
```

**`site/llms.txt`** — add a line under `## Knowledge centre`, in the same shape as the others:

```
- [Article title](https://arcubus.in/knowledge/your-slug.html): what the article covers, in one clause.
```

**`site/llms-full.txt`** — optional but worth it: paste the article's plain text at the end under
a `---` divider with a `# Title` and `URL:` line, matching the existing pattern.

Commit, push, done. Ping the URL through Search Console's **URL Inspection → Request indexing**
if you want it picked up the same day.

### Publishing checklist

- [ ] Slug reads like a search query
- [ ] Title, description, canonical, og:url all point at the new file
- [ ] JSON-LD: headline, description, dates, URL, section, breadcrumb
- [ ] `<h1>` is sentence case and ends in a full stop
- [ ] Key takeaways box answers the question in bullet one
- [ ] FAQ visible text matches the FAQ JSON-LD exactly
- [ ] Card added at the top of `knowledge-centre.html`
- [ ] `sitemap.xml` and `llms.txt` updated
- [ ] Opened the page in a browser and clicked every link
- [ ] The copied file has no leftover `REPLACE` text and no `noindex` meta tag

---

## 4. Updating the team section

Open `site/our-people.html`. Two things to update, and they must agree with each other.

### 4a. The visible cards

Each person is one block, in `<div class="grid g3">`:

```html
<div class="person">
<div class="monogram"><img src="assets/icons/person.svg" alt="" width="22" height="22"></div>
<h3>[Name]</h3>
<p class="role">Director &amp; Co-founder</p>
<p>[Qualification · years of experience — profile to be added.]</p>
<div class="pillrow"><span class="pill">Benchmarking method and review</span></div>
</div>
```

- **Name** — in the `<h3>`.
- **Role** — Title Case (`Manager — TP Benchmarking`). Use `&amp;` for an ampersand in HTML.
- **Bio** — two or three sentences: where the TP experience was built, which jurisdictions and
  transaction types, what they lead here. Keep every bio a similar length; ragged card heights
  look careless.
- **Pills** — one to three focus areas, a few words each.

**To use initials instead of the person icon**, replace the monogram line with:

```html
<div class="monogram">RS</div>
```

**To use a photograph**: save it into `site/assets/team/` as a square JPG, at least 400×400,
then replace the monogram line with:

```html
<img class="monogram" src="assets/team/firstname-lastname.jpg" alt="Firstname Lastname" width="56" height="56" style="object-fit:cover">
```

Use photos for everyone or nobody — a mixed row looks unfinished.

**To add a person**: copy an entire `<div class="person">…</div>` block and edit it. The grid
handles any number; rows of three fill left to right, so six or nine people look tidiest.
**To remove one**: delete the whole block, opening tag to closing tag.

### 4b. The Person schema

In the `<head>` JSON-LD there is one `"@type": "Person"` object per team member. Keep it in sync:

```json
{
  "@type": "Person",
  "name": "Full Name",
  "jobTitle": "Manager — TP Benchmarking",
  "worksFor": { "@id": "https://arcubus.in/#organization" },
  "knowsAbout": ["TNMM and CUP studies", "Internal review gate"]
}
```

Add a LinkedIn profile with `"sameAs": ["https://www.linkedin.com/in/…"]` — it is the strongest
signal that a named person is real, which matters for how assistants describe the firm.

If you add or remove someone, **also** update the "In short" box at the top of the page
(`[X] directors … [X] managers … [X] analysts`) and the answer to "How is the team qualified?"
in the FAQ — including its copy in the `FAQPage` JSON-LD.

---

## 5. Wiring up Zoho

Both integrations are already in `site/contact.html` with placeholder values. Each has a dashed
red TODO note next to it on the page; **delete that note once the values are in**.

### 5a. Contact form → Zoho CRM (Web-to-Lead)

1. In Zoho CRM: **Setup → Developer Space → Webforms → Create form → Leads**.
2. Drag in the fields you want (see the mapping below), then set:
   - **Landing page URL:** `https://arcubus.in/thank-you.html`
   - **reCAPTCHA:** on, if you want spam protection (see the note below)
   - **Assign lead owner** and any workflow / notification rule
3. Click **Save → Embed code**. In the code Zoho gives you, find these two lines and copy the
   `value` from each:
   - `name="xnQsjsdp"` — your owner ID
   - `name="xmIwtLD"` — your form ID
4. In `site/contact.html`, replace `ZOHO_OWNER_ID` and `ZOHO_FORM_ID` with those values.
5. Leave everything else in the form alone. Zoho matches leads on the field `name` attributes, so
   `name="Last Name"`, `name="Company"`, `name="Email"` etc. must stay exactly as written.

Current field mapping (rename the labels freely; do not rename the `name` attributes):

| Form field | Zoho lead field |
| --- | --- |
| First name / Last name | First Name / Last Name (Last Name is mandatory in Zoho) |
| Firm / company | Company |
| Work email | Email |
| Phone | Phone |
| You are | Industry |
| What do you need | Lead Status |
| Transaction, jurisdictions and deadline | Description |
| (hidden) | Lead Source = `Website — Contact form` |

If you prefer custom Zoho fields for "You are" and "What do you need", create them in CRM, note
their `LEADCF<n>` API names from the embed code, and swap the two `name` attributes.

**Test it:** submit the form once from the live domain, confirm a lead appears in CRM and that you
land on `/thank-you.html`. Then delete the test lead.

**If you enable reCAPTCHA** or Zoho's own spam field, take the extra `<input>` and `<script>` lines
from Zoho's embed code and paste them inside the `<form>` element, just above the submit button —
that is the one case where a script belongs in a page body.

### 5b. "Book a call" → Zoho Bookings

1. In Zoho Bookings, create the service (e.g. *30-minute TP scoping call*), set your availability,
   duration, buffer and time zone, and connect the calendar that should receive the events.
2. Open **Services → your service → Share → Embed**, and copy the embed URL. It looks like
   `https://yourportal.zohobookings.in/portal-embed#/1234567890abcdef`.
3. In `site/contact.html`, in the `<iframe>` inside `<section id="book">`, replace:
   - `ZOHO_PORTAL` with your portal name
   - `ZOHO_SERVICE_ID` with the ID after `portal-embed#/`
   - the domain — `.zohobookings.in` for the India data centre, `.zohobookings.com` for the US,
     `.eu` / `.com.au` accordingly. Copy whatever Zoho shows you.
4. Optional but recommended: in Bookings, set the confirmation email and add a Zoho CRM
   integration so a booking also creates or updates the lead.

The section has the id `book`, so `contact.html#book` scrolls straight to the scheduler — that is
what every "Schedule a consultation" button on the site already points to.

**Note on the iframe:** it loads with `loading="lazy"`, so it does not slow the page down. If it
shows blank on the live domain, the cause is almost always that the service is not published, or
the data-centre domain is wrong.

---

## 6. Filling in the bracketed placeholders

Text in `[square brackets]` is a deliberate placeholder — brand policy is to show a gap rather
than invent a fact. Before launch, sweep them all. Search your editor for `[` across `site/`.

**Appears in every page** (inside the JSON-LD `ProfessionalService` block) — use find-and-replace
across all files so they stay identical:

| Placeholder | Where else it shows |
| --- | --- |
| `[Street address]`, `[PIN]` | contact.html office block |
| `[email@arcubus.in]` | contact.html (3 places), thank-you.html |
| `[+91 00000 00000]` and `[+910000000000]` | contact.html phone line (`tel:` needs no spaces) |
| `[https://www.linkedin.com/company/arcubus-advisors]` | contact.html LinkedIn line |
| `[Founder name]` | JSON-LD `founder` |

**Page by page:**

- `index.html` — the databases you subscribe to; turnaround days in the FAQ
- `services.html` — managed-services hours per month; fee bands if you want them public
- `process.html` — working days for preliminary results and final report; file retention period
- `who-we-serve.html` — your data-handling and access policy
- `our-people.html` — every name, bio, `[X]` count and the qualification-mix answer
- `case-studies.html` — every `[X]`; delete any line you cannot substantiate
- `contact.html` — office hours, reply time, Zoho IDs
- `knowledge-centre.html` — your publishing cadence

When you change a fact that appears in an FAQ answer, change it in **both** the visible text and
the `FAQPage` JSON-LD.

---

## 7. Editing without breaking things

**The nav and footer are in every file.** To add a page to the nav you must edit the
`<div class="navlinks">` block in all 14 HTML files (and the footer link lists). Copy one block
and paste it into the others rather than retyping. This duplication is the price of having no
build step and no JavaScript — it is what makes the site fast and fully readable by crawlers.

**Marking the current page.** The nav link for the page you are on carries
`aria-current="page"` — that is what draws the red underline. When you copy a nav block between
pages, move the attribute to the right link.

**Safe to change freely:** any text between tags, `<li>` items, card blocks, table rows,
chips (`<span class="chip">…</span>`), FAQ items.

**Do not touch:** `class` attribute values, the `assets/tokens/` folder, the `name` attributes on
the Zoho form, `support`-level structure like `<main id="main">`.

**Check before you push:** open the file in a browser. Look for an unclosed tag (everything after
it collapses), a missing `</div>` (layout jumps), or `&` written raw instead of `&amp;`.

**Adding a whole new page:** copy the closest existing page, change the head block, the nav
`aria-current`, and the body — then add it to `sitemap.xml`, `llms.txt`, the nav in all files, and
the footer.

---

## 8. What keeps this site visible — and why

The site is optimised for two different readers. Both matter now.

**Search engines** get: server-rendered HTML with no JS dependency, one `<h1>` per page, a unique
title and description on every page, canonical tags, clean semantic markup, `sitemap.xml`,
`robots.txt`, fast static delivery from Vercel's CDN, and JSON-LD structured data
(`ProfessionalService`, `Service`, `Article`, `FAQPage`, `HowTo`, `BreadcrumbList`, `Person`,
`DefinedTermSet`).

**AI assistants** (ChatGPT, Claude, Perplexity, Copilot, Google AI overviews) get: `llms.txt` and
`llms-full.txt`, an explicit crawler allow-list in `robots.txt`, an **answer-first summary box** at
the top of every page, FAQ blocks written as literal question → answer pairs, a glossary for
definition queries, and a comparison page for "X vs Y" queries. Assistants quote self-contained
sentences; that is why the takeaway bullets and FAQ answers are written to stand alone.

**Five habits that keep it working**

1. **One page per question.** If a topic needs a different `<h1>`, it needs a different page.
2. **Answer in the first sentence.** In the summary box, in each FAQ answer, in each takeaway.
3. **Be specific and verifiable.** "Within 1 working day" beats "fast turnaround" for both
   readers. Numbers, method names and jurisdictions are what get quoted.
4. **Keep JSON-LD in sync with visible text.** Structured data that contradicts the page is worse
   than none.
5. **Publish on a cadence you can hold.** One good note a month beats six in a week and then
   silence. Update `dateModified` when you revise an old article — refreshed pages get re-crawled.

**Do not** add keyword-stuffed paragraphs, hidden text, doorway pages for each city, or
AI-generated filler. This site's advantage is that a practitioner wrote it; that is also what
makes assistants cite it.

---

## 9. Quick reference

| I want to… | File to open |
| --- | --- |
| Publish an article | copy `knowledge/_TEMPLATE-article.html`, then `knowledge-centre.html`, `sitemap.xml`, `llms.txt` |
| Add or edit a team member | `our-people.html` (card **and** Person JSON-LD) |
| Change the phone, email or address | find-and-replace across all files in `site/` |
| Connect the contact form | `contact.html` → `ZOHO_OWNER_ID`, `ZOHO_FORM_ID` |
| Connect the booking scheduler | `contact.html` → `ZOHO_PORTAL`, `ZOHO_SERVICE_ID` |
| Add a glossary term | `glossary.html` (visible `<div class="term">` **and** `DefinedTerm` JSON-LD) |
| Add a case study | `case-studies.html` (copy a whole `<section>`) |
| Change a service description | `services.html` (and the matching `Service` JSON-LD) |
| Change site-wide styling | `assets/site.css` — never `assets/tokens/` |
| Add a redirect after renaming a page | `vercel.json` → `redirects` |
