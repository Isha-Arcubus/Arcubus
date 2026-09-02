#!/usr/bin/env python3
"""
Arcubus local admin tool
Creates a new knowledge article from _TEMPLATE-article.html
"""

from pathlib import Path
from datetime import datetime
import os
import re
import sys

# ====== PATHS (matches your structure) ======
REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "site" / "knowledge" / "_TEMPLATE-article.html"
OUTPUT_DIR = REPO_ROOT / "site" / "knowledge"
# ============================================

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def main():
    print("=" * 55)
    print("  Arcubus – Create New Knowledge Article")
    print("=" * 55)
    print()

    if not TEMPLATE_PATH.exists():
        print(f"❌ Template not found:\n   {TEMPLATE_PATH}")
        sys.exit(1)

    # ---------- Collect required data ----------
    title = input("1. Article Title (headline):\n> ").strip()
    if not title:
        print("Title is required.")
        return

    suggested_slug = slugify(title)
    slug = input(f"\n2. Filename / slug (without .html) [{suggested_slug}]:\n> ").strip() or suggested_slug
    slug = slug.lower().replace(" ", "-")
    if slug.endswith(".html"):
        slug = slug[:-5]

    category = input("\n3. Category (e.g. Benchmarking, Documentation, OECD):\n> ").strip() or "Transfer Pricing"

    today = datetime.now()
    date_iso = input(f"\n4. Publish date (YYYY-MM-DD) [{today.strftime('%Y-%m-%d')}]:\n> ").strip() or today.strftime("%Y-%m-%d")
    
    try:
        date_obj = datetime.strptime(date_iso, "%Y-%m-%d")
        date_human = date_obj.strftime("%-d %B %Y")          # 1 January 2027
    except:
        date_human = date_iso

    description = input("\n5. Meta description (150-160 chars):\n> ").strip()
    if not description:
        description = f"{title} — practical guidance from Arcubus Advisors."

    read_time = input("\n6. Estimated read time (e.g. 6 min read) [6 min read]:\n> ").strip() or "6 min read"

    print("\n7. Key takeaways (enter 3–5 points, one per line).")
    print("   Finish with an empty line:")
    takeaways = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        takeaways.append(line)
    if not takeaways:
        takeaways = ["Key point one.", "Key point two.", "Key point three."]

    print("\n8. Main body content (HTML is fine).")
    print("   Paste everything that should go inside <div class=\"prose\">.")
    print("   Finish with an empty line + Enter (or Ctrl+D):")
    body_lines = []
    try:
        while True:
            line = input()
            if line.strip() == "" and body_lines:
                break
            body_lines.append(line)
    except EOFError:
        pass
    body = "\n".join(body_lines).strip() or "<p>REPLACE — body content here.</p>"

    # Optional FAQ
    print("\n9. FAQ (optional). Press Enter to skip.")
    faq_q1 = input("   Question 1: ").strip()
    faq_a1 = input("   Answer 1  : ").strip() if faq_q1 else ""
    faq_q2 = input("   Question 2: ").strip()
    faq_a2 = input("   Answer 2  : ").strip() if faq_q2 else ""

    # ---------- Load template ----------
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    # ---------- Perform replacements ----------
    # Title / headline
    html = html.replace("REPLACE — Article title", title)
    html = html.replace("REPLACE — Headline in sentence case, ending in a full stop.", title if title.endswith(".") else title + ".")

    # Slug / URLs
    html = html.replace("REPLACE-your-slug", slug)

    # Description
    html = html.replace("REPLACE — 150-160 character summary that answers the article’s question. This is what appears in search results and in AI answers.", description)
    html = html.replace("REPLACE — summary", description)

    # Dates
    html = html.replace("REPLACE — 2027-01-01", date_iso)
    html = html.replace("REPLACE — 1 January 2027", date_human)

    # Category
    html = html.replace("REPLACE — Category", category)

    # Read time
    html = html.replace("REPLACE — 6 min read", read_time)

    # Key takeaways (Isolates and replaces the exact template lists cleanly)
    old_takeaways = """<li>REPLACE — the answer to the article’s question, in one sentence.</li>
<li>REPLACE — the second point a reader must leave with.</li>
<li>REPLACE — the third.</li>"""
    new_takeaways = "\n".join(f"<li>{t}</li>" for t in takeaways)
    html = html.replace(old_takeaways, new_takeaways)

    # Body content (Isolates and replaces the exact prose template code blocks)
    old_body = """<p>REPLACE — opening paragraph. State the problem in the first two sentences; no scene-setting.</p>
<h2>REPLACE — first section heading.</h2>
<p>REPLACE — body text.</p>
<ul>
<li><strong>REPLACE</strong> — list items use a bold lead-in then an em dash.</li>
<li><strong>REPLACE</strong> — keep to five items or fewer.</li>
</ul>
<h2>REPLACE — second section heading.</h2>"""
    html = html.replace(old_body, body)

    # FAQ (simple version)
    # if faq_q1:
    #     html = html.replace("REPLACE — a question a client actually asks, phrased the way they say it?", faq_q1)
    #     html = html.replace("REPLACE — answer it directly in the first sentence, then add the qualification. This text must match the FAQPage JSON-LD in the head.", faq_a1)
    #     html = html.replace('"name": "REPLACE — a question a client actually asks, phrased the way they say it?"', f'"name": "{faq_q1}"')
    #     html = html.replace('"text": "REPLACE — answer it directly in the first sentence, then add the qualification."', f'"text": "{faq_a1}"')

    # if faq_q2:
    #     html = html.replace("REPLACE — second question?", faq_q2)
    #     html = html.replace("REPLACE — answer.", faq_a2)
    #     html = html.replace('"name": "REPLACE — second question?"', f'"name": "{faq_q2}"')
    #     html = html.replace('"text": "REPLACE — answer."', f'"text": "{faq_a2}"')


        # --------------------------------------------------
    # FAQ (Updated to match your backup template classes)
    # --------------------------------------------------
    if faq_q1:
        html = html.replace("REPLACE — a question a client actually asks, phrased the way they say it?", faq_q1)
        html = html.replace("REPLACE — answer it directly in the first sentence, then add the qualification. This text must match the FAQPage JSON-LD in the head.", faq_a1)
        html = html.replace('"name": "REPLACE — a question a client actually asks, phrased the way they say it?"', f'"name": "{faq_q1}"')
        html = html.replace('"text": "REPLACE — answer it directly in the first sentence, then add the qualification."', f'"text": "{faq_a1}"')
    else:
        # Removes first FAQ item block if left blank
        html = html.replace(
            """<div class="item">\n<h3>REPLACE — a question a client actually asks, phrased the way they say it?</h3>\n<p>REPLACE — answer it directly in the first sentence, then add the qualification. This text must match the FAQPage JSON-LD in the head.</p>\n</div>""", 
            ""
        )

    if faq_q2:
        html = html.replace("REPLACE — second question?", faq_q2)
        html = html.replace("REPLACE — answer.", faq_a2)
        html = html.replace('"name": "REPLACE — second question?"', f'"name": "{faq_q2}"')
        html = html.replace('"text": "REPLACE — answer."', f'"text": "{faq_a2}"')
    else:
        # Removes second FAQ item block if left blank
        html = html.replace(
            """<div class="item">\n<h3>REPLACE — second question?</h3>\n<p>REPLACE — answer.</p>\n</div>""", 
            ""
        )


    # ---------- Write file ----------
    output_path = OUTPUT_DIR / f"{slug}.html"

    if output_path.exists():
        overwrite = input(f"\n⚠️  File already exists: {slug}.html\nOverwrite? (y/N): ").strip().lower()
        if overwrite != "y":
            print("Cancelled.")
            return

    output_path.write_text(html, encoding="utf-8")
    print(f"\n✅ Article created:")
    print(f"   {output_path}")

    # ---------- Git ----------
    print()
    do_git = input("Run git add + commit + push now? (y/N): ").strip().lower()
    if do_git == "y":
        os.chdir(REPO_ROOT)
        rel = output_path.relative_to(REPO_ROOT)
        os.system(f'git add "{rel}"')
        os.system(f'git commit -m "Add knowledge article: {title}"')
        os.system("git push")
        print("\n🚀 Pushed. Vercel will rebuild automatically.")
    else:
        print("\nLater you can run:")
        print(f'  git add site/knowledge/{slug}.html')
        print(f'  git commit -m "Add knowledge article: {title}"')
        print("  git push")

if __name__ == "__main__":
    main()

