# Arcubus Advisors — website

Static marketing site for [arcubus.in](https://arcubus.in). Plain HTML, no build step, no
framework, no JavaScript rendering — every page is served complete on the first request, which
is what makes it fast, fully crawlable by Google, and readable by AI assistants.

**Deployable folder: `site/`** — set that as the Root Directory in Vercel.

## Deploy to Vercel

### Option A — Git (recommended: every push auto-deploys)

1. Create an empty repository on GitHub and push this folder to it:
   ```bash
   git init
   git add .
   git commit -m "Arcubus Advisors website"
   git branch -M main
   git remote add origin git@github.com:<you>/arcubus-website.git
   git push -u origin main
   ```
2. In Vercel: **Add New → Project → Import** the repository.
3. On the configure screen:
   - **Framework Preset:** `Other`
   - **Root Directory:** `site` ← the one setting that matters
   - **Build Command:** leave empty
   - **Output Directory:** leave empty
4. **Deploy.** You get a `*.vercel.app` URL in under a minute.

### Option B — CLI, no Git

```bash
npm i -g vercel
cd site
vercel          # preview deployment
vercel --prod   # production
```

Answer "no" when asked to override the build settings.

### Option C — drag and drop

Zip the **contents** of `site/` (not the folder itself) and drop it on
[vercel.com/new](https://vercel.com/new). Fine for a one-off; use Option A for anything you
intend to keep updating.

## Connect the domain

Vercel → Project → **Settings → Domains** → add `arcubus.in` and `www.arcubus.in`. Vercel prints
the DNS records to create at your registrar (an `A` record for the apex, a `CNAME` for `www`).
Keep `arcubus.in` as primary and let `www` redirect to it — the canonical tags in the HTML
already point at `https://arcubus.in`.

## After the first production deploy

1. **Fill in the bracketed placeholders.** Text in `[square brackets]` is a deliberate gap
   awaiting a confirmed fact — address, email, phone, turnaround days, team bios. Search for `[`
   across `site/`. Full list: `UPDATING-THE-WEBSITE.md` § 6.
2. **Wire up Zoho.** The contact form (CRM Web-to-Lead) and the booking scheduler (Zoho Bookings)
   are live but carry `ZOHO_OWNER_ID`, `ZOHO_FORM_ID`, `ZOHO_PORTAL` and `ZOHO_SERVICE_ID`
   placeholders, each with a visible red TODO note on the page. Steps: § 5 of the guide.
3. **Submit the sitemap** — `https://arcubus.in/sitemap.xml` — to
   [Google Search Console](https://search.google.com/search-console) and
   [Bing Webmaster Tools](https://www.bing.com/webmasters). Do not skip Bing: its index is what
   Copilot and several AI assistants read from.
4. **Verify the machine files** load in a browser: `/robots.txt`, `/sitemap.xml`, `/llms.txt`,
   `/llms-full.txt`.

## Updating the site

Edit a file → commit → push. Vercel redeploys in 20–40 seconds, and every push also gets its own
preview URL so you can check an article before it hits the live domain.

**`UPDATING-THE-WEBSITE.md` is the operating manual** — the 9-step article workflow with a
publishing checklist, the team-section procedure, Zoho wiring, the placeholder sweep, and the
editing rules that keep the design system intact. Read § 3 before publishing your first article.

## What is in `site/`

14 pages: home, services, who we serve, process, knowledge centre + 3 articles + a copy-me
article template, glossary, in-house vs outsourced comparison, case studies, our people, contact,
thank-you, 404.

Machine-facing files: `robots.txt` (with an explicit AI-crawler allow-list), `sitemap.xml`,
`llms.txt`, `llms-full.txt`, and `vercel.json` (caching, security headers, redirects).

`assets/site.css` holds all styling, built on the Arcubus design-system tokens in
`assets/tokens/` — **never edit the tokens folder**. `assets/site.js` is the only script on the
site and does one thing: the mobile nav toggle.
