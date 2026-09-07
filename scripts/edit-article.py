# #!/usr/bin/env python3
# """
# Arcubus local admin tool
# Edits an existing knowledge article to fix typos or update text
# """

# from pathlib import Path
# import os
# import sys

# # ====== PATHS (matches your creation script structure) ======
# REPO_ROOT = Path(__file__).resolve().parent.parent
# OUTPUT_DIR = REPO_ROOT / "site" / "knowledge"
# # ============================================================

# def main():
#     print("=" * 55)
#     print("  Arcubus – Edit Existing Knowledge Article")
#     print("=" * 55)
#     print()

#     # 1. Locate and list available files to edit
#     if not OUTPUT_DIR.exists():
#         print(f"❌ Knowledge directory not found:\n   {OUTPUT_DIR}")
#         sys.exit(1)

#     # Gather all HTML files, ignoring template files
#     articles = [f for f in OUTPUT_DIR.glob("*.html") if not f.name.startswith("_")]
    
#     if not articles:
#         print(f"No articles found in {OUTPUT_DIR}")
#         return

#     print("Available articles:")
#     for idx, article in enumerate(articles, start=1):
#         print(f"  [{idx}] {article.name}")

#     # 2. Select the file
#     try:
#         choice = input("\nSelect the article number to edit:\n> ").strip()
#         file_idx = int(choice) - 1
#         if file_idx < 0 or file_idx >= len(articles):
#             raise ValueError
#         selected_file = articles[file_idx]
#     except (ValueError, IndexError):
#         print("Invalid selection. Exiting.")
#         return

#     # 3. Read the article content
#     html = selected_file.read_text(encoding="utf-8")

#     # 4. Get the typo target and its replacement
#     print(f"\nSelected: {selected_file.name}")
#     typo = input("Enter the typo or text you want to replace:\n> ").strip()
#     if not typo:
#         print("Target text cannot be empty.")
#         return

#     # Verify if the typo target exists in the file before continuing
#     count = html.count(typo)
#     if count == 0:
#         print(f"❌ Could not find any instances of '{typo}' in this file.")
#         return
    
#     print(f"Found {count} instance(s) of '{typo}'.")
#     correction = input("\nEnter the correct text replacement:\n> ").strip()

#     # 5. Execute replacement and preview
#     updated_html = html.replace(typo, correction)
    
#     print("\n--- Summary of Changes ---")
#     print(f"Original: {typo}")
#     print(f"Replaced: {correction}")
#     print("--------------------------")

#     confirm = input(f"Apply changes to {selected_file.name}? (y/N): ").strip().lower()
#     if confirm != "y":
#         print("Cancelled. No changes written.")
#         return

#     # 6. Overwrite the file cleanly using UTF-8
#     selected_file.write_text(updated_html, encoding="utf-8")
#     print(f"\n✅ Successfully updated {selected_file.name}")

#     # 7. Integrated Git Engine Automation (matches your deployment flow)
#     print()
#     do_git = input("Run git add + commit + push now? (y/N): ").strip().lower()
#     if do_git == "y":
#         os.chdir(REPO_ROOT)
#         os.system("git add .")
#         os.system(f'git commit -m "Fix: Correct typo in article {selected_file.name}"')
#         os.system("git push")
#         print("\n🚀 Pushed successfully. Vercel deployment initialized.")

# if __name__ == "__main__":
#     main()



#!/usr/bin/env python3
"""
Arcubus local admin tool
Edits an existing knowledge article to fix typos or update text (Multi-edit version)
"""

from pathlib import Path
import os
import sys

# ====== PATHS (matches your creation script structure) ======
REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "site" / "knowledge"
# ============================================================

def main():
    print("=" * 55)
    print("  Arcubus – Edit Existing Knowledge Article")
    print("=" * 55)
    print()

    # 1. Locate and list available files to edit
    if not OUTPUT_DIR.exists():
        print(f"❌ Knowledge directory not found:\n   {OUTPUT_DIR}")
        sys.exit(1)

    # Gather all HTML files, ignoring template files
    articles = [f for f in OUTPUT_DIR.glob("*.html") if not f.name.startswith("_")]
    
    if not articles:
        print(f"No articles found in {OUTPUT_DIR}")
        return

    print("Available articles:")
    for idx, article in enumerate(articles, start=1):
        print(f"  [{idx}] {article.name}")

    # 2. Select the file
    try:
        choice = input("\nSelect the article number to edit:\n> ").strip()
        file_idx = int(choice) - 1
        if file_idx < 0 or file_idx >= len(articles):
            raise ValueError
        selected_file = articles[file_idx]
    except (ValueError, IndexError):
        print("Invalid selection. Exiting.")
        return

    # 3. Read the initial article content
    html = selected_file.read_text(encoding="utf-8")
    original_html = html  # Keep a backup in case they want to cancel everything
    
    print(f"\nSelected: {selected_file.name}")
    
    # 4. Multi-edit Loop
    has_changes = False
    while True:
        print("\n--- New Edit ---")
        typo = input("Enter the typo or text you want to replace:\n> ").strip()
        if not typo:
            print("Target text cannot be empty.")
            continue

        # Verify if the typo target exists in the current version of the file
        count = html.count(typo)
        if count == 0:
            print(f"❌ Could not find any instances of '{typo}' in this file.")
        else:
            print(f"Found {count} instance(s) of '{typo}'.")
            correction = input("Enter the correct text replacement:\n> ").strip()
            
            # Apply change in memory
            html = html.replace(typo, correction)
            has_changes = True
            print(f"✅ Replaced '{typo}' with '{correction}' in memory.")

        # Ask if the user has more mistakes to fix
        another = input("\nIs there another mistake to fix in this article? (y/N): ").strip().lower()
        if another != "y":
            break

    # 5. Review and Save Changes
    if not has_changes:
        print("\nNo changes made. Exiting.")
        return

    print(f"\nAll edits completed for {selected_file.name}.")
    confirm = input("Save all changes to the file? (y/N): ").strip().lower()
    if confirm != "y":
        print("Cancelled. Changes abandoned.")
        return

    # Overwrite the file cleanly using UTF-8
    selected_file.write_text(html, encoding="utf-8")
    print(f"\n💾 Successfully updated {selected_file.name}")

    # 6. Integrated Git Engine Automation
    print()
    do_git = input("Run git add + commit + push now? (y/N): ").strip().lower()
    if do_git == "y":
        os.chdir(REPO_ROOT)
        os.system("git add .")
        os.system(f'git commit -m "Fix: Correct multiple typos in article {selected_file.name}"')
        os.system("git push")
        print("\n🚀 Pushed successfully. Vercel deployment initialized.")

if __name__ == "__main__":
    main()
