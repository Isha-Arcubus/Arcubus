#!/usr/bin/env python3
"""
Arcubus Site Publishing and Synchronization Utilities.
Handles:
1. Registering new knowledge articles into site/knowledge-centre.html
2. Updating site/sitemap.xml
3. Reliable Git staging, commit, and push operations with clean feedback.
"""

from pathlib import Path
import re
import subprocess
import os

def update_knowledge_centre(repo_root: Path, slug: str, title: str, category: str, description: str, date_human: str, date_iso: str, read_time: str) -> bool:
    """
    Inserts or updates the article card in site/knowledge-centre.html
    and updates the Schema.org JSON-LD blogPost array.
    """
    kc_path = repo_root / "site" / "knowledge-centre.html"
    if not kc_path.exists():
        print(f"Warning: {kc_path} does not exist.")
        return False

    content = kc_path.read_text(encoding="utf-8")
    article_href = f"knowledge/{slug}.html"
    card_html = f'<a class="articlecard" href="{article_href}"><span class="tag">{category}</span><h3>{title}</h3><p>{description}</p><span class="date">{date_human} · {read_time}</span></a>'

    # 1. Update or insert the article card inside <div class="grid g3">
    pattern = re.compile(rf'<a class="articlecard" href="{re.escape(article_href)}">.*?</a>', re.DOTALL)
    if pattern.search(content):
        content = pattern.sub(card_html, content)
    else:
        grid_marker = '<div class="grid g3">'
        if grid_marker in content:
            content = content.replace(grid_marker, f"{grid_marker}\n{card_html}", 1)
        else:
            print("Warning: '<div class=\"grid g3\">' not found in knowledge-centre.html")

    # 2. Update or insert the JSON-LD blogPost entry
    post_url = f"https://arcubus.in/knowledge/{slug}.html"
    clean_desc = description.replace('"', '\\"').replace('\n', ' ')
    clean_title = title.replace('"', '\\"')

    blogpost_block = f'''        {{
          "@type": "BlogPosting",
          "headline": "{clean_title}",
          "url": "{post_url}",
          "datePublished": "{date_iso}",
          "description": "{clean_desc}",
          "author": {{
            "@id": "https://arcubus.in/#organization"
          }}
        }}'''

    if f'"{post_url}"' not in content:
        blogpost_marker = '"blogPost": ['
        if blogpost_marker in content:
            content = content.replace(blogpost_marker, f'{blogpost_marker}\n{blogpost_block},', 1)

    kc_path.write_text(content, encoding="utf-8")

    # 3. Update sitemap.xml
    update_sitemap(repo_root, slug, date_iso)
    return True


def update_sitemap(repo_root: Path, slug: str, date_iso: str):
    """Updates or inserts url entry in site/sitemap.xml"""
    sitemap_path = repo_root / "site" / "sitemap.xml"
    if not sitemap_path.exists():
        return

    content = sitemap_path.read_text(encoding="utf-8")
    url_loc = f"https://arcubus.in/knowledge/{slug}.html"

    if url_loc in content:
        pattern = re.compile(rf'(<loc>{re.escape(url_loc)}</loc>\s*<lastmod>)[^<]+(</lastmod>)')
        if pattern.search(content):
            content = pattern.sub(rf'\g<1>{date_iso}\g<2>', content)
            sitemap_path.write_text(content, encoding="utf-8")
    else:
        entry = f"""  <url>
    <loc>{url_loc}</loc>
    <lastmod>{date_iso}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>"""
        content = content.replace("</urlset>", entry)
        sitemap_path.write_text(content, encoding="utf-8")


def run_git_push(repo_root: Path, commit_message: str) -> tuple:
    """
    Runs git add, commit, and push in the repo_root directory.
    Returns (success: bool, message: str).
    """
    try:
        add_res = subprocess.run(
            ["git", "add", "."],
            cwd=str(repo_root),
            capture_output=True,
            text=True
        )
        if add_res.returncode != 0:
            return False, f"Git add failed:\n{add_res.stderr or add_res.stdout}"

        status_res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root),
            capture_output=True,
            text=True
        )
        if not status_res.stdout.strip():
            return True, "No new changes detected to commit."

        commit_res = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=str(repo_root),
            capture_output=True,
            text=True
        )
        if commit_res.returncode != 0:
            return False, f"Git commit failed:\n{commit_res.stderr or commit_res.stdout}"

        push_res = subprocess.run(
            ["git", "push"],
            cwd=str(repo_root),
            capture_output=True,
            text=True
        )
        if push_res.returncode != 0:
            err_msg = push_res.stderr or push_res.stdout
            return False, f"Git push failed:\n{err_msg}"

        return True, f"Pushed successfully to GitHub!\n\nCommit: {commit_message}"

    except Exception as ex:
        return False, f"Unexpected error during git execution:\n{ex}"
