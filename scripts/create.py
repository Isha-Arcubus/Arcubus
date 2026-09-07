#!/usr/bin/env python3
"""
Arcubus local admin tool
Creates a new knowledge article from _TEMPLATE-article.html 
with smart multi-block text and image alignment workflows
"""

from pathlib import Path
from datetime import datetime
import os
import re
import sys
import shutil

# ====== PATHS (matches your structure) ======
REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "site" / "knowledge" / "_TEMPLATE-article.html"
OUTPUT_DIR = REPO_ROOT / "site" / "knowledge"

# Target destination for article images inside your existing assets structure
IMAGE_DEST_DIR = REPO_ROOT / "site" / "assets" / "images" 
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
        day = str(date_obj.day)
        date_human = f"{day} {date_obj.strftime('%B %Y')}"
    except:
        date_human = date_iso

    description = input("\n5. Meta description (150-160 chars):\n> ").strip()
    if not description:
        description = f"{title} — practical guidance from Arcubus Advisors."

    lede = input("\n6. Article Lede Paragraph (1-2 lines displayed below headline):\n> ").strip()
    if not lede:
        lede = f"Selecting the right transfer pricing method for intra-group services is critical to achieving an arm’s-length outcome."

    read_time = input("\n7. Estimated read time (e.g. 6 min read) [6 min read]:\n> ").strip() or "6 min read"

    print("\n8. Key takeaways (enter 3–5 points, one per line).")
    print("   Finish with an empty line:")
    takeaways = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        takeaways.append(line)
    if not takeaways:
        takeaways = ["Key point one.", "Key point two.", "Key point three."]
    takeaways_html = "\n".join(f"<li>{t}</li>" for t in takeaways)


    # ---------- 9. Smart Main Body Content Builder ----------        
    print("\n9. Build main body content.")
    print("   Add paragraphs, subheadings, or copy over images dynamically with alignment rules.")
    
    body_blocks = []
    IMAGE_DEST_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        print("\nChoose what type of content block to add:")
        print("  [p] Paragraph text")
        print("  [h] Subheading (H2)")
        print("  [i] Image File (With Layout Alignment Configurations)")
        print("  [f] Finished building content")
        
        choice = input("> ").strip().lower()
        
        if choice == 'p':
            text = input("Enter paragraph text:\n> ").strip()
            if text:
                body_blocks.append(f"<p>{text}</p>")
                
        elif choice == 'h':
            heading = input("Enter subheading text:\n> ").strip()
            if heading:
                body_blocks.append(f"<h2>{heading}</h2>")
                
        elif choice == 'i':
            img_path_str = input("Drag & drop image file here (or type path):\n> ").strip().strip("'\"")
            img_path = Path(img_path_str)
            
            if not img_path.exists() or not img_path.is_file():
                print("❌ Error: Image file not found. Block skipped.")
                continue
                
            # Copy image file to assets structure
            dest_image_path = IMAGE_DEST_DIR / img_path.name
            try:
                shutil.copy2(img_path, dest_image_path)
                print(f"📸 Image successfully moved to asset tree: site/assets/images/{img_path.name}")
                
                alt_text = input("Enter image descriptive Alt text (optional):\n> ").strip() or title
                
                # Image Alignment Processing Choice Menu
                print("\nChoose image layout style:")
                print("  [l] Left aligned (text wraps tightly around the right side)")
                print("  [r] Right aligned (text wraps tightly around the left side)")
                print("  [c] Centered block (no wrapping, text breaks cleanly underneath)")
                align_choice = input("> ").strip().lower()
                
                if align_choice == 'l':
                    align_class = "img-align-left"
                elif align_choice == 'r':
                    align_class = "img-align-right"
                else:
                    align_class = "img-align-center"
                
                # Construct HTML structure string and save to the building container stack
                img_html = f'<img src="../assets/images/{img_path.name}" alt="{alt_text}" class="{align_class}" />'
                body_blocks.append(img_html)
                print(f"✅ Added image block successfully with '{align_class}' styling.")
                
            except Exception as e:
                print(f"❌ Failed to process image: {e}")
                
        elif choice == 'f':
            break
        else:
            print("Invalid selection. Please enter p, h, i, or f.")

    body = "\n".join(body_blocks).strip() or "<p>REPLACE — body content here.</p>"


    # ---------- Optional FAQ ----------
    print("\n10. FAQ (optional). Press Enter to skip.")
    faq_q1 = input("   Question 1: ").strip()
    faq_a1 = input("   Answer 1  : ").strip() if faq_q1 else ""
    faq_q2 = input("   Question 2: ").strip()
    faq_a2 = input("   Answer 2  : ").strip() if faq_q2 else ""

    # ---------- Load template ----------
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    # ---------- Perform Standard Text Swaps ----------
    html = html.replace("REPLACE — Article title", title)
    html = html.replace("REPLACE — Headline in sentence case, ending in a full stop.", title if title.endswith(".") else title + ".")
    html = html.replace("REPLACE-your-slug", slug)
    html = html.replace("REPLACE — summary", description)
    html = html.replace("REPLACE — 2027-01-01", date_iso)
    html = html.replace("REPLACE — 1 January 2027", date_human)
    html = html.replace("REPLACE — Category", category)
    html = html.replace("REPLACE — 6 min read", read_time)
    html = html.replace("REPLACE — topic", category)
    html = html.replace("REPLACE — one or two sentences saying what the reader will be able to do after reading. Keep under 58 characters per line of measure; the CSS handles the wrapping.", lede)

    html = html.replace("REPLACE_TAKEAWAYS_MARKER", takeaways_html)
    html = html.replace("REPLACE_BODY_MARKER", body)

    # FAQ Processing Loops
    if faq_q1:
        html = html.replace("REPLACE — a question a client actually asks, phrased the way they say it?", faq_q1)
        html = html.replace("REPLACE — answer it directly in the first sentence, then add the qualification. This text must match the FAQPage JSON-LD in the head.", faq_a1)
        html = html.replace('"name": "REPLACE — a question a client actually asks, phrased the way they say it?"', f'"name": "{faq_q1}"')
        html = html.replace('"text": "REPLACE — answer it directly in the first sentence, then add the qualification."', f'"text": "{faq_a1}"')
    else:
        html = html.replace("""    <div class="item">\n        <h3>REPLACE — a question a client actually asks, phrased the way they say it?</h3>\n        <p>REPLACE — answer it directly in the first sentence, then add the qualification. This text must match the FAQPage JSON-LD in the head.</p>\n    </div>""", "")

    if faq_q2:
        html = html.replace("REPLACE — second question?", faq_q2)
        html = html.replace("REPLACE — answer.", faq_a2)
        html = html.replace('"name": "REPLACE — second question?"', f'"name": "{faq_q2}"')
        html = html.replace('"text": "REPLACE — answer."', f'"text": "{faq_a2}"')
    else:
        html = html.replace("""    <div class="item">\n        <h3>REPLACE — second question?</h3>\n        <p>REPLACE — answer.</p>\n    </div>""", "")

    # ---------- Write file ----------
    output_path = OUTPUT_DIR / f"{slug}.html"

    if output_path.exists():
        overwrite = input(f"\n⚠️  File already exists: {slug}.html\nOverwrite? (y/N): ").strip().lower()
        if overwrite != "y":
            print("Cancelled.")
            return

    output_path.write_text(html, encoding="utf-8")
    print(f"\n✅ Perfect complete article created at:")
    print(f"   {output_path}")

    # ---------- Integrated Git Engine Automation ----------
    print()
    do_git = input("Run git add + commit + push now? (y/N): ").strip().lower()
    if do_git == "y":
        os.chdir(REPO_ROOT)
        os.system("git add .")
        os.system(f'git commit -m "Feat: Add knowledge article with updated footer and structure: {title}"')
        os.system("git push")
        print("\n🚀 Pushed successfully. Vercel deployment initialized.")

if __name__ == "__main__":
    main()
