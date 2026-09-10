
#!/usr/bin/env python3
"""
Arcubus Desktop Admin Dashboard
Upgraded Interface supporting mixed storyboards (text/images) and FAQ arrays
"""

import sys
import os
import shutil
import re
import json
from html import escape
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from people_manager import (
    PeopleManagerError,
    list_people,
    add_person,
    update_person,
    delete_person,
)


# =========================================================
# PATH SETUP
# =========================================================

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

SITE_DIR = os.path.abspath(
    os.path.join(SCRIPTS_DIR, "..", "site")
)

index_page = os.path.join(SITE_DIR, "index.html")
knowledge_folder = os.path.join(SITE_DIR, "knowledge")

REPO_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_DIR = REPO_ROOT / "site" / "knowledge"
IMAGE_DEST_DIR = REPO_ROOT / "site" / "assets" / "images"

ARTICLE_TEMPLATE = KNOWLEDGE_DIR / "_TEMPLATE-article.html"

KNOWLEDGE_CENTRE_PATH = REPO_ROOT / "site" / "knowledge-centre.html"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


class ArcubusAdminApp:

    def __init__(self, root):
        self.root = root

        self.root.title("Arcubus – Website Content Manager Pro")
        self.root.geometry("900x800")
        self.root.minsize(800, 600)

        self.style = ttk.Style()
        self.style.theme_use("vista" if os.name == "nt" else "clam")

        self.storyboard_items = []

        # self.notebook = ttk.Notebook(self.root)
        # self.notebook.pack(
        #     fill="both",
        #     expand=True,
        #     padx=10,
        #     pady=10
        # )
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(10, 0)
        )

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(
            fill="both",
            expand=True
        )

        self.build_article_tab()
        self.build_edit_tab()
        self.build_people_tab()
        self.build_git_panel()

    # =========================================================
    # TAB 1: CREATE NEW KNOWLEDGE ARTICLE
    # =========================================================

    def build_article_tab(self):

        tab = ttk.Frame(self.notebook)

        self.notebook.add(
            tab,
            text=" 📝 Create New Article "
        )

        canvas = tk.Canvas(
            tab,
            borderwidth=0,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            tab,
            orient="vertical",
            command=canvas.yview
        )

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.art_title = tk.StringVar()
        self.art_category = tk.StringVar(
            value="Transfer Pricing"
        )
        self.art_read_time = tk.StringVar(
            value="6 min read"
        )

        ttk.Label(
            self.scrollable_frame,
            text="Article Metadata",
            font=("Segoe UI", 12, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(10, 5)
        )

        ttk.Label(
            self.scrollable_frame,
            text="Article Title / Headline:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=5
        )

        ttk.Entry(
            self.scrollable_frame,
            textvariable=self.art_title,
            width=70
        ).grid(
            row=1,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            self.scrollable_frame,
            text="Category / Topic:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=5
        )

        ttk.Entry(
            self.scrollable_frame,
            textvariable=self.art_category,
            width=30
        ).grid(
            row=2,
            column=1,
            sticky="w"
        )

        ttk.Label(
            self.scrollable_frame,
            text="Read Time:"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=5
        )

        ttk.Entry(
            self.scrollable_frame,
            textvariable=self.art_read_time,
            width=20
        ).grid(
            row=3,
            column=1,
            sticky="w"
        )

        ttk.Label(
            self.scrollable_frame,
            text="Lede Paragraph:"
        ).grid(
            row=4,
            column=0,
            sticky="nw",
            pady=5
        )

        self.art_lede = tk.Text(
            self.scrollable_frame,
            width=70,
            height=3,
            wrap="word"
        )

        self.art_lede.grid(
            row=4,
            column=1,
            columnspan=2,
            sticky="w",
            pady=5
        )

        self.art_lede.insert(
            "1.0",
            "Selecting the right transfer pricing method for intra-group services is critical to achieving an arm’s-length outcome."
        )

        ttk.Label(
            self.scrollable_frame,
            text="Meta Description:"
        ).grid(
            row=5,
            column=0,
            sticky="nw",
            pady=5
        )

        self.art_desc = tk.Text(
            self.scrollable_frame,
            width=70,
            height=2,
            wrap="word"
        )

        self.art_desc.grid(
            row=5,
            column=1,
            columnspan=2,
            sticky="w",
            pady=5
        )

        ttk.Label(
            self.scrollable_frame,
            text="Key Takeaways (one per line):"
        ).grid(
            row=6,
            column=0,
            sticky="nw",
            pady=5
        )

        self.art_takeaways = tk.Text(
            self.scrollable_frame,
            width=70,
            height=4,
            wrap="word"
        )

        self.art_takeaways.grid(
            row=6,
            column=1,
            columnspan=2,
            sticky="w",
            pady=5
        )

        self.art_takeaways.insert(
            "1.0",
            "Key point one.\nKey point two.\nKey point three."
        )

        ttk.Separator(
            self.scrollable_frame,
            orient="horizontal"
        ).grid(
            row=7,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=15
        )

        ttk.Label(
            self.scrollable_frame,
            text="Article Content Builder (Add in any order)",
            font=("Segoe UI", 12, "bold")
        ).grid(
            row=8,
            column=0,
            columnspan=3,
            sticky="w",
            pady=5
        )

        control_deck = ttk.Frame(
            self.scrollable_frame
        )

        control_deck.grid(
            row=9,
            column=0,
            columnspan=3,
            sticky="w",
            pady=10
        )

        ttk.Button(
            control_deck,
            text="➕ Add Paragraph",
            command=self.add_paragraph_block
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            control_deck,
            text="➕ Add Subheading (H2)",
            command=self.add_heading_block
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            control_deck,
            text="➕ Add Image Asset",
            command=self.add_image_block
        ).pack(
            side="left",
            padx=5
        )

        self.storyboard_container = ttk.Frame(
            self.scrollable_frame
        )

        self.storyboard_container.grid(
            row=10,
            column=0,
            columnspan=3,
            sticky="w",
            pady=5
        )

        self.add_paragraph_block()

        ttk.Separator(
            self.scrollable_frame,
            orient="horizontal"
        ).grid(
            row=11,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=15
        )

        ttk.Label(
            self.scrollable_frame,
            text="Questions / FAQ Accordions (Optional)",
            font=("Segoe UI", 12, "bold")
        ).grid(
            row=12,
            column=0,
            columnspan=3,
            sticky="w",
            pady=5
        )

        ttk.Label(
            self.scrollable_frame,
            text="FAQ Question 1:"
        ).grid(
            row=13,
            column=0,
            sticky="w",
            pady=5
        )

        self.faq_q1 = tk.Entry(
            self.scrollable_frame,
            width=70
        )

        self.faq_q1.grid(
            row=13,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            self.scrollable_frame,
            text="FAQ Answer 1:"
        ).grid(
            row=14,
            column=0,
            sticky="w",
            pady=5
        )

        self.faq_a1 = tk.Entry(
            self.scrollable_frame,
            width=70
        )

        self.faq_a1.grid(
            row=14,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            self.scrollable_frame,
            text="FAQ Question 2:"
        ).grid(
            row=15,
            column=0,
            sticky="w",
            pady=5
        )

        self.faq_q2 = tk.Entry(
            self.scrollable_frame,
            width=70
        )

        self.faq_q2.grid(
            row=15,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            self.scrollable_frame,
            text="FAQ Answer 2:"
        ).grid(
            row=16,
            column=0,
            sticky="w",
            pady=5
        )

        self.faq_a2 = tk.Entry(
            self.scrollable_frame,
            width=70
        )

        self.faq_a2.grid(
            row=16,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Button(
            self.scrollable_frame,
            text="🚀 Build and Save Complete Article",
            command=self.process_article
        ).grid(
            row=17,
            column=1,
            pady=30,
            sticky="w"
        )

    # =========================================================
    # STORYBOARD
    # =========================================================

    def add_paragraph_block(self):

        row_frame = ttk.LabelFrame(
            self.storyboard_container,
            text=" Paragraph Component Block "
        )

        row_frame.pack(
            fill="x",
            expand=True,
            pady=5
        )

        txt_box = tk.Text(
            row_frame,
            width=75,
            height=4,
            wrap="word"
        )

        txt_box.pack(
            side="left",
            padx=10,
            pady=10
        )

        item_data = {
            "type": "p",
            "widget": txt_box,
            "frame": row_frame
        }

        ttk.Button(
            row_frame,
            text="❌ Remove",
            command=lambda: self.remove_storyboard_item(
                row_frame,
                item_data
            )
        ).pack(
            side="right",
            padx=10
        )

        self.storyboard_items.append(item_data)

    def add_heading_block(self):

        row_frame = ttk.LabelFrame(
            self.storyboard_container,
            text=" Subheading (H2) Component Block "
        )

        row_frame.pack(
            fill="x",
            expand=True,
            pady=5
        )

        entry = tk.Entry(
            row_frame,
            width=60
        )

        entry.pack(
            side="left",
            padx=10,
            pady=10
        )

        item_data = {
            "type": "h",
            "widget": entry,
            "frame": row_frame
        }

        ttk.Button(
            row_frame,
            text="❌ Remove",
            command=lambda: self.remove_storyboard_item(
                row_frame,
                item_data
            )
        ).pack(
            side="right",
            padx=10
        )

        self.storyboard_items.append(item_data)

    def add_image_block(self):

        row_frame = ttk.LabelFrame(
            self.storyboard_container,
            text=" Image Layout Asset Block "
        )

        row_frame.pack(
            fill="x",
            expand=True,
            pady=5
        )

        path_var = tk.StringVar()
        align_var = tk.StringVar(value="c")

        path_frame = ttk.Frame(row_frame)

        path_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        ttk.Label(
            path_frame,
            text="File Path:"
        ).pack(
            side="left"
        )

        ttk.Entry(
            path_frame,
            textvariable=path_var,
            width=50
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            path_frame,
            text="Browse...",
            command=lambda: self.browse_file(path_var)
        ).pack(
            side="left"
        )

        align_frame = ttk.Frame(row_frame)

        align_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        ttk.Radiobutton(
            align_frame,
            text="Center Block",
            variable=align_var,
            value="c"
        ).pack(
            side="left",
            padx=5
        )

        ttk.Radiobutton(
            align_frame,
            text="Left Wrap",
            variable=align_var,
            value="l"
        ).pack(
            side="left",
            padx=5
        )

        ttk.Radiobutton(
            align_frame,
            text="Right Wrap",
            variable=align_var,
            value="r"
        ).pack(
            side="left",
            padx=5
        )

        item_data = {
            "type": "i",
            "path": path_var,
            "align": align_var,
            "frame": row_frame
        }

        ttk.Button(
            row_frame,
            text="❌ Remove",
            command=lambda: self.remove_storyboard_item(
                row_frame,
                item_data
            )
        ).pack(
            side="right",
            padx=10,
            pady=5
        )

        self.storyboard_items.append(item_data)

    def remove_storyboard_item(self, frame, item_data):

        frame.destroy()

        if item_data in self.storyboard_items:
            self.storyboard_items.remove(item_data)

    # =========================================================
    # TAB 2: EDIT ARTICLE
    # =========================================================

    def build_edit_tab(self):

        tab = ttk.Frame(self.notebook)

        self.notebook.add(
            tab,
            text=" 🔍 Edit Existing Article "
        )

        ttk.Label(
            tab,
            text="Interactive Article Correction & Image Replacement",
            font=("Segoe UI", 12, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=15,
            padx=15
        )

        ttk.Label(
            tab,
            text="1. Select Target HTML File:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=5,
            padx=15
        )

        self.edit_file_box = ttk.Combobox(
            tab,
            width=45,
            state="readonly"
        )

        self.edit_file_box.grid(
            row=1,
            column=1,
            sticky="w"
        )

        ttk.Button(
            tab,
            text="🔄 Refresh List",
            command=self.refresh_articles_list
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=5
        )

        ttk.Label(
            tab,
            text="2. Text Error to Find:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=10,
            padx=15
        )

        self.edit_typo = tk.Entry(
            tab,
            width=48
        )

        self.edit_typo.grid(
            row=2,
            column=1,
            sticky="w"
        )

        ttk.Label(
            tab,
            text="3. Correct Replacement Text:"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=5,
            padx=15
        )

        self.edit_correction = tk.Entry(
            tab,
            width=48
        )

        self.edit_correction.grid(
            row=3,
            column=1,
            sticky="w"
        )

        ttk.Button(
            tab,
            text="⚡ Apply One Text Correction",
            command=self.apply_typo_correction
        ).grid(
            row=4,
            column=1,
            pady=10,
            sticky="w"
        )

        ttk.Separator(
            tab,
            orient="horizontal"
        ).grid(
            row=5,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=15,
            pady=10
        )

        ttk.Label(
            tab,
            text="Optional: Replace a Wrong Image",
            font=("Segoe UI", 11, "bold")
        ).grid(
            row=6,
            column=0,
            columnspan=3,
            sticky="w",
            padx=15,
            pady=5
        )

        ttk.Label(
            tab,
            text="4. Current Image Filename:"
        ).grid(
            row=7,
            column=0,
            sticky="w",
            pady=5,
            padx=15
        )

        self.edit_old_image = tk.Entry(
            tab,
            width=48
        )

        self.edit_old_image.grid(
            row=7,
            column=1,
            sticky="w"
        )

        ttk.Label(
            tab,
            text="5. Replacement Image:"
        ).grid(
            row=8,
            column=0,
            sticky="w",
            pady=5,
            padx=15
        )

        self.edit_new_image = tk.StringVar()

        ttk.Entry(
            tab,
            textvariable=self.edit_new_image,
            width=40
        ).grid(
            row=8,
            column=1,
            sticky="w"
        )

        ttk.Button(
            tab,
            text="Browse...",
            command=self.browse_image_for_edit
        ).grid(
            row=8,
            column=2,
            sticky="w",
            padx=5
        )

        ttk.Button(
            tab,
            text="🖼 Replace Image",
            command=self.replace_article_image
        ).grid(
            row=9,
            column=1,
            pady=10,
            sticky="w"
        )

        ttk.Label(
            tab,
            text="Current Session Changes:"
        ).grid(
            row=10,
            column=0,
            sticky="nw",
            pady=5,
            padx=15
        )

        self.edit_log = tk.Text(
            tab,
            width=58,
            height=8,
            state="disabled",
            wrap="word",
            background="#f0f0f0"
        )

        self.edit_log.grid(
            row=10,
            column=1,
            columnspan=2,
            sticky="w",
            pady=5
        )

        self.btn_save_edits = ttk.Button(
            tab,
            text="💾 Write and Finalize All Changes To Disk",
            state="disabled",
            command=self.save_final_edits
        )

        self.btn_save_edits.grid(
            row=11,
            column=1,
            pady=15,
            sticky="w"
        )

        self.refresh_articles_list()

        self.active_edit_html = ""
        self.active_file_path = None

    # =========================================================
    # PEOPLE TAB
    # =========================================================

    def build_people_tab(self):

        tab = ttk.Frame(self.notebook)

        self.notebook.add(
            tab,
            text=" 👥 Manage Our People "
        )

        canvas = tk.Canvas(
            tab,
            borderwidth=0,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            tab,
            orient="vertical",
            command=canvas.yview
        )

        frame = ttk.Frame(canvas)

        frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0),
            window=frame,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.people_frame = frame

        ttk.Label(
            frame,
            text="Our People Manager",
            font=("Segoe UI", 12, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=15,
            pady=(15, 5)
        )

        ttk.Label(
            frame,
            text="Add, edit, delete and replace profile images without manually editing our-people.html."
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            padx=15,
            pady=(0, 15)
        )

        ttk.Label(
            frame,
            text="EDIT EXISTING PERSON",
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="w",
            padx=15,
            pady=(5, 8)
        )

        ttk.Label(
            frame,
            text="Select Person:"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.people_selector = ttk.Combobox(
            frame,
            width=55,
            state="readonly"
        )

        self.people_selector.grid(
            row=3,
            column=1,
            sticky="w",
            pady=5
        )

        self.people_selector.bind(
            "<<ComboboxSelected>>",
            self.load_selected_person
        )

        ttk.Button(
            frame,
            text="🔄 Refresh",
            command=self.refresh_people_list
        ).grid(
            row=3,
            column=2,
            sticky="w",
            padx=5
        )

        ttk.Label(
            frame,
            text="Name:"
        ).grid(
            row=4,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.person_name = tk.Entry(
            frame,
            width=58
        )

        self.person_name.grid(
            row=4,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            frame,
            text="Designation:"
        ).grid(
            row=5,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.person_role = tk.Entry(
            frame,
            width=58
        )

        self.person_role.grid(
            row=5,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            frame,
            text="Profile / Experience:"
        ).grid(
            row=6,
            column=0,
            sticky="nw",
            padx=15,
            pady=5
        )

        self.person_bio = tk.Text(
            frame,
            width=58,
            height=5,
            wrap="word"
        )

        self.person_bio.grid(
            row=6,
            column=1,
            columnspan=2,
            sticky="w",
            pady=5
        )

        ttk.Label(
            frame,
            text="Expertise 1:"
        ).grid(
            row=7,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.person_expertise1 = tk.Entry(
            frame,
            width=58
        )

        self.person_expertise1.grid(
            row=7,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            frame,
            text="Expertise 2:"
        ).grid(
            row=8,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.person_expertise2 = tk.Entry(
            frame,
            width=58
        )

        self.person_expertise2.grid(
            row=8,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            frame,
            text="Current Profile Image:"
        ).grid(
            row=9,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.person_current_image = tk.StringVar(
            value="Not loaded"
        )

        ttk.Label(
            frame,
            textvariable=self.person_current_image
        ).grid(
            row=9,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            frame,
            text="New Profile Image:"
        ).grid(
            row=10,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.person_new_image = tk.StringVar()

        ttk.Entry(
            frame,
            textvariable=self.person_new_image,
            width=45
        ).grid(
            row=10,
            column=1,
            sticky="w"
        )

        ttk.Button(
            frame,
            text="Browse...",
            command=self.browse_people_image
        ).grid(
            row=10,
            column=2,
            sticky="w",
            padx=5
        )

        self.person_default_image = tk.BooleanVar(
            value=False
        )

        ttk.Checkbutton(
            frame,
            text="Use default person icon instead",
            variable=self.person_default_image
        ).grid(
            row=11,
            column=1,
            sticky="w",
            pady=3
        )

        people_edit_buttons = ttk.Frame(frame)

        people_edit_buttons.grid(
            row=12,
            column=1,
            columnspan=2,
            sticky="w",
            pady=10
        )

        ttk.Button(
            people_edit_buttons,
            text="✏️ Update Person",
            command=self.update_selected_person
        ).pack(
            side="left",
            padx=(0, 8)
        )

        ttk.Button(
            people_edit_buttons,
            text="🗑️ Delete Person",
            command=self.delete_selected_person
        ).pack(
            side="left"
        )

        ttk.Separator(
            frame,
            orient="horizontal"
        ).grid(
            row=13,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=15,
            pady=15
        )

        ttk.Label(
            frame,
            text="ADD NEW PERSON",
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=14,
            column=0,
            columnspan=3,
            sticky="w",
            padx=15,
            pady=5
        )

        ttk.Label(
            frame,
            text="Name:"
        ).grid(
            row=15,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.add_person_name = tk.Entry(
            frame,
            width=58
        )

        self.add_person_name.grid(
            row=15,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            frame,
            text="Designation:"
        ).grid(
            row=16,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.add_person_role = tk.Entry(
            frame,
            width=58
        )

        self.add_person_role.grid(
            row=16,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            frame,
            text="Profile / Experience:"
        ).grid(
            row=17,
            column=0,
            sticky="nw",
            padx=15,
            pady=5
        )

        self.add_person_bio = tk.Text(
            frame,
            width=58,
            height=5,
            wrap="word"
        )

        self.add_person_bio.grid(
            row=17,
            column=1,
            columnspan=2,
            sticky="w",
            pady=5
        )

        ttk.Label(
            frame,
            text="Expertise 1:"
        ).grid(
            row=18,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.add_person_expertise1 = tk.Entry(
            frame,
            width=58
        )

        self.add_person_expertise1.grid(
            row=18,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            frame,
            text="Expertise 2:"
        ).grid(
            row=19,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.add_person_expertise2 = tk.Entry(
            frame,
            width=58
        )

        self.add_person_expertise2.grid(
            row=19,
            column=1,
            columnspan=2,
            sticky="w"
        )

        ttk.Label(
            frame,
            text="Profile Image (optional):"
        ).grid(
            row=20,
            column=0,
            sticky="w",
            padx=15,
            pady=5
        )

        self.add_person_image = tk.StringVar()

        ttk.Entry(
            frame,
            textvariable=self.add_person_image,
            width=45
        ).grid(
            row=20,
            column=1,
            sticky="w"
        )

        ttk.Button(
            frame,
            text="Browse...",
            command=self.browse_add_person_image
        ).grid(
            row=20,
            column=2,
            sticky="w",
            padx=5
        )

        ttk.Button(
            frame,
            text="➕ Add New Person",
            command=self.add_new_person
        ).grid(
            row=21,
            column=1,
            sticky="w",
            pady=15
        )

        self.refresh_people_list()

    # =========================================================
    # PEOPLE HELPERS
    # =========================================================

    def _clear_person_fields(self):

        for entry in (
            self.person_name,
            self.person_role,
            self.person_expertise1,
            self.person_expertise2,
        ):
            entry.delete(0, tk.END)

        self.person_bio.delete(
            "1.0",
            tk.END
        )

        self.person_new_image.set("")
        self.person_current_image.set(
            "Not loaded"
        )

        self.person_default_image.set(False)

    def refresh_people_list(self):

        try:
            people = list_people()

        except PeopleManagerError as e:
            messagebox.showerror(
                "People Page Error",
                str(e)
            )
            return

        values = [
            f"{p['index'] + 1}. {p['name']} — {p['role']}"
            for p in people
        ]

        self.people_selector["values"] = values

        if values:
            self.people_selector.current(0)
            self.load_selected_person()

    def load_selected_person(self, event=None):

        try:
            people = list_people()

        except PeopleManagerError as e:
            messagebox.showerror(
                "People Page Error",
                str(e)
            )
            return

        index = self.people_selector.current()

        if index < 0 or index >= len(people):
            return

        person = people[index]

        self.person_name.delete(0, tk.END)
        self.person_name.insert(
            0,
            person["name"]
        )

        self.person_role.delete(0, tk.END)
        self.person_role.insert(
            0,
            person["role"]
        )

        self.person_bio.delete(
            "1.0",
            tk.END
        )

        self.person_bio.insert(
            "1.0",
            person["profile"]
        )

        self.person_expertise1.delete(
            0,
            tk.END
        )

        self.person_expertise1.insert(
            0,
            person.get("expertise1", "")
        )

        self.person_expertise2.delete(
            0,
            tk.END
        )

        self.person_expertise2.insert(
            0,
            person.get("expertise2", "")
        )

        self.person_current_image.set(
            person.get("image")
            or "assets/icons/person.svg"
        )

        self.person_new_image.set("")
        self.person_default_image.set(False)

    def browse_people_image(self):

        filename = filedialog.askopenfilename(
            filetypes=[
                (
                    "Image Files",
                    "*.png *.jpg *.jpeg *.webp *.gif"
                )
            ]
        )

        if filename:
            self.person_new_image.set(filename)

    def browse_add_person_image(self):

        filename = filedialog.askopenfilename(
            filetypes=[
                (
                    "Image Files",
                    "*.png *.jpg *.jpeg *.webp *.gif"
                )
            ]
        )

        if filename:
            self.add_person_image.set(filename)

    def update_selected_person(self):

        index = self.people_selector.current()

        if index < 0:
            messagebox.showerror(
                "Error",
                "Please select a person."
            )
            return

        name = self.person_name.get().strip()
        role = self.person_role.get().strip()
        bio = self.person_bio.get(
            "1.0",
            "end"
        ).strip()

        expertise1 = self.person_expertise1.get().strip()
        expertise2 = self.person_expertise2.get().strip()
        image_path = self.person_new_image.get().strip()

        try:

            backup = update_person(
                index,
                name,
                role,
                bio,
                expertise1,
                expertise2,
                image_path=image_path,
                use_default_image=self.person_default_image.get(),
            )

            messagebox.showinfo(
                "Updated",
                f"Person updated successfully.\n\n"
                f"our-people.html was updated.\n"
                f"Backup created:\n{backup.name}"
            )

            self.refresh_people_list()

        except PeopleManagerError as e:

            messagebox.showerror(
                "Update Failed",
                str(e)
            )

    def add_new_person(self):

        name = self.add_person_name.get().strip()
        role = self.add_person_role.get().strip()

        bio = self.add_person_bio.get(
            "1.0",
            "end"
        ).strip()

        expertise1 = self.add_person_expertise1.get().strip()
        expertise2 = self.add_person_expertise2.get().strip()
        image_path = self.add_person_image.get().strip()

        try:

            backup = add_person(
                name,
                role,
                bio,
                expertise1,
                expertise2,
                image_path=image_path,
            )

            messagebox.showinfo(
                "Person Added",
                f"New person added successfully.\n\n"
                f"our-people.html was updated.\n"
                f"Backup created:\n{backup.name}"
            )

            self.add_person_name.delete(
                0,
                tk.END
            )

            self.add_person_role.delete(
                0,
                tk.END
            )

            self.add_person_bio.delete(
                "1.0",
                tk.END
            )

            self.add_person_expertise1.delete(
                0,
                tk.END
            )

            self.add_person_expertise2.delete(
                0,
                tk.END
            )

            self.add_person_image.set("")

            self.refresh_people_list()

        except PeopleManagerError as e:

            messagebox.showerror(
                "Add Failed",
                str(e)
            )

    def delete_selected_person(self):

        index = self.people_selector.current()

        if index < 0:
            messagebox.showerror(
                "Error",
                "Please select a person."
            )
            return

        try:

            people = list_people()

            if index >= len(people):
                messagebox.showerror(
                    "Error",
                    "Selected person no longer exists."
                )
                return

            person = people[index]

            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Delete this person from the Our People page?\n\n"
                f"{person['name']} — {person['role']}\n\n"
                f"This will remove the visible card and its Person JSON-LD entry."
            )

            if not confirm:
                return

            backup = delete_person(index)

            messagebox.showinfo(
                "Deleted",
                f"{person['name']} was removed successfully.\n\n"
                f"Backup created:\n{backup.name}"
            )

            self.refresh_people_list()

        except PeopleManagerError as e:

            messagebox.showerror(
                "Delete Failed",
                str(e)
            )

    # =========================================================
    # GIT PANEL
    # =========================================================

    def build_git_panel(self):

        panel = ttk.LabelFrame(
            self.root,
            text=" Global Deployment Engine "
        )

        panel.pack(
            fill="x",
            side="bottom",
            padx=15,
            pady=10
        )

        self.git_commit_msg = tk.StringVar(
            value="Content update to knowledge center articles"
        )

        ttk.Label(
            panel,
            text="Git Commit Message:"
        ).pack(
            side="left",
            padx=10,
            pady=10
        )

        ttk.Entry(
            panel,
            textvariable=self.git_commit_msg,
            width=55
        ).pack(
            side="left",
            padx=5,
            fill="x",
            expand=True,
            pady=10
        )

        ttk.Button(
            panel,
            text="🚀 Push Changes to GitHub",
            command=self.trigger_git_engine
        ).pack(
            side="right",
            padx=10,
            pady=10
        )

    # =========================================================
    # CORE UTILITIES
    # =========================================================

    def browse_file(self, target_var):

        filename = filedialog.askopenfilename(
            filetypes=[
                (
                    "Image Files",
                    "*.png *.jpg *.jpeg *.webp *.gif"
                )
            ]
        )

        if filename:
            target_var.set(filename)

    def refresh_articles_list(self):

        if KNOWLEDGE_DIR.exists():

            files = [
                f.name
                for f in KNOWLEDGE_DIR.glob("*.html")
                if not f.name.startswith("_")
            ]

            self.edit_file_box["values"] = files

            if files:
                self.edit_file_box.current(0)

        else:

            self.edit_file_box["values"] = [
                "Missing knowledge directory Layout Tree"
            ]

    def log_message(self, message):

        self.edit_log.config(
            state="normal"
        )

        self.edit_log.insert(
            "end",
            message + "\n"
        )

        self.edit_log.config(
            state="disabled"
        )

        self.edit_log.see("end")

    # =========================================================
    # CREATE ARTICLE
    # =========================================================

    def process_article(self):

        title = self.art_title.get().strip()

        if not title:

            messagebox.showerror(
                "Error",
                "Article Title headline context is required."
            )

            return

        slug = slugify(title)

        category = self.art_category.get().strip()
        read_time = self.art_read_time.get().strip()

        lede = self.art_lede.get(
            "1.0",
            "end"
        ).strip()

        desc = (
            self.art_desc.get(
                "1.0",
                "end"
            ).strip()
            or f"{title} — practical guidance from Arcubus Advisors."
        )

        tk_list = [
            t.strip()
            for t in self.art_takeaways.get(
                "1.0",
                "end"
            ).split("\n")
            if t.strip()
        ]

        takeaways_html = "\n".join(
            f"<li>{t}</li>"
            for t in tk_list
        )

        # -----------------------------------------------------
        # COMPILE STORYBOARD
        # -----------------------------------------------------

        compiled_body_blocks = []

        for item in self.storyboard_items:

            if item["type"] == "p":

                val = item["widget"].get(
                    "1.0",
                    "end"
                ).strip()

                if val:
                    compiled_body_blocks.append(
                        f"<p>{val}</p>"
                    )

            elif item["type"] == "h":

                val = item["widget"].get().strip()

                if val:
                    compiled_body_blocks.append(
                        f"<h2>{val}</h2>"
                    )

            elif item["type"] == "i":

                img_str = item["path"].get().strip()

                if img_str:

                    img_path = Path(img_str)

                    if img_path.exists():

                        IMAGE_DEST_DIR.mkdir(
                            parents=True,
                            exist_ok=True
                        )

                        shutil.copy2(
                            img_path,
                            IMAGE_DEST_DIR / img_path.name
                        )

                        align = item["align"].get()

                        if align == "l":
                            align_class = "img-align-left"

                        elif align == "r":
                            align_class = "img-align-right"

                        else:
                            align_class = "img-align-center"

                        compiled_body_blocks.append(
                            f'<img src="../assets/images/{img_path.name}" '
                            f'alt="{title}" '
                            f'class="{align_class}" />'
                        )

        body_text = "\n".join(
            compiled_body_blocks
        ).strip()

        # -----------------------------------------------------
        # TEMPLATE
        # -----------------------------------------------------

        if not ARTICLE_TEMPLATE.exists():

            messagebox.showerror(
                "Error",
                f"Missing template structure mapping:\n"
                f"{ARTICLE_TEMPLATE}"
            )

            return

        html = ARTICLE_TEMPLATE.read_text(
            encoding="utf-8"
        )

        html = html.replace(
            "REPLACE — Article title",
            title
        )

        html = html.replace(
            "REPLACE — Headline in sentence case, ending in a full stop.",
            title if title.endswith(".") else title + "."
        )

        html = html.replace(
            "REPLACE-your-slug",
            slug
        )

        html = html.replace(
            "REPLACE — summary",
            desc
        )

        html = html.replace(
            "REPLACE — Category",
            category
        )

        html = html.replace(
            "REPLACE — topic",
            category
        )

        html = html.replace(
            "REPLACE — 6 min read",
            read_time
        )

        html = html.replace(
            "REPLACE — one or two sentences saying what the reader will be able to do after reading. Keep under 58 characters per line of measure; the CSS handles the wrapping.",
            lede
        )

        today = datetime.now()

        html = html.replace(
            "REPLACE — 2027-01-01",
            today.strftime("%Y-%m-%d")
        )

        html = html.replace(
            "REPLACE — 1 January 2027",
            today.strftime("%d %B %Y")
        )

        html = html.replace(
            "REPLACE_TAKEAWAYS_MARKER",
            takeaways_html
        )

        html = html.replace(
            "REPLACE_BODY_MARKER",
            body_text
        )

        # -----------------------------------------------------
        # FAQ
        # -----------------------------------------------------

        q1 = self.faq_q1.get().strip()
        a1 = self.faq_a1.get().strip()

        q2 = self.faq_q2.get().strip()
        a2 = self.faq_a2.get().strip()

        if q1:

            html = html.replace(
                "REPLACE — a question a client actually asks, phrased the way they say it?",
                q1
            )

            html = html.replace(
                "REPLACE — answer it directly in the first sentence, then add the qualification. This text must match the FAQPage JSON-LD in the head.",
                a1
            )

            html = html.replace(
                '"name": "REPLACE — a question a client actually asks, phrased the way they say it?"',
                f'"name": "{q1}"'
            )

            html = html.replace(
                '"text": "REPLACE — answer it directly in the first sentence, then add the qualification."',
                f'"text": "{a1}"'
            )

        else:

            html = html.replace(
                """    <div class="item">
        <h3>REPLACE — a question a client actually asks, phrased the way they say it?</h3>
        <p>REPLACE — answer it directly in the first sentence, then add the qualification. This text must match the FAQPage JSON-LD in the head.</p>
    </div>""",
                ""
            )

        if q2:

            html = html.replace(
                "REPLACE — second question?",
                q2
            )

            html = html.replace(
                "REPLACE — answer.",
                a2
            )

            html = html.replace(
                '"name": "REPLACE — second question?"',
                f'"name": "{q2}"'
            )

            html = html.replace(
                '"text": "REPLACE — answer."',
                f'"text": "{a2}"'
            )

        else:

            html = html.replace(
                """    <div class="item">
        <h3>REPLACE — second question?</h3>
        <p>REPLACE — answer.</p>
    </div>""",
                ""
            )

        # -----------------------------------------------------
        # SAVE NEW ARTICLE
        # -----------------------------------------------------

        out_path = KNOWLEDGE_DIR / f"{slug}.html"

        out_path.write_text(
            html,
            encoding="utf-8"
        )

        # =====================================================
        # UPDATE KNOWLEDGE CENTRE PAGE
        # =====================================================

        knowledge_centre_path = (
            REPO_ROOT
            / "site"
            / "knowledge-centre.html"
        )

        if knowledge_centre_path.exists():

            knowledge_centre_html = (
                knowledge_centre_path.read_text(
                    encoding="utf-8"
                )
            )

            safe_title = escape(title)
            safe_category = escape(category)
            safe_lede = escape(lede)
            safe_read_time = escape(read_time)

            today = datetime.now()

            display_date = today.strftime(
                "%d %B %Y"
            )

            iso_date = today.strftime(
                "%Y-%m-%d"
            )

            # -------------------------------------------------
            # CREATE ARTICLE CARD
            # -------------------------------------------------

            new_article_card = f'''<a class="articlecard" href="knowledge/{slug}.html">
<span class="tag">{safe_category}</span>
<h3>{safe_title}</h3>
<p>{safe_lede}</p>
<span class="date">{display_date} · {safe_read_time}</span>
</a>'''

            article_grid_marker = (
                '<div class="grid g3">'
            )

            article_already_exists = (
                f'href="knowledge/{slug}.html"'
                in knowledge_centre_html
            )

            if not article_already_exists:

                if article_grid_marker in knowledge_centre_html:

                    knowledge_centre_html = (
                        knowledge_centre_html.replace(
                            article_grid_marker,
                            article_grid_marker
                            + "\n"
                            + new_article_card,
                            1
                        )
                    )

                else:

                    messagebox.showwarning(
                        "Knowledge Centre",
                        "Article was created, but the article "
                        "grid could not be found in "
                        "knowledge-centre.html."
                    )

            # -------------------------------------------------
            # BLOGPOST JSON-LD
            # -------------------------------------------------

            if not article_already_exists:

                new_blog_post = {
                    "@type": "BlogPosting",
                    "headline": title,
                    "url": (
                        f"https://arcubus.in/"
                        f"knowledge/{slug}.html"
                    ),
                    "datePublished": iso_date,
                    "description": lede,
                    "author": {
                        "@id": (
                            "https://arcubus.in/"
                            "#organization"
                        )
                    }
                }

                new_blog_post_json = json.dumps(
                    new_blog_post,
                    ensure_ascii=False,
                    indent=10
                )

                blogpost_marker = '"blogPost": ['

                if blogpost_marker in knowledge_centre_html:

                    knowledge_centre_html = (
                        knowledge_centre_html.replace(
                            blogpost_marker,
                            blogpost_marker
                            + "\n          "
                            + new_blog_post_json
                            + ",",
                            1
                        )
                    )

                else:

                    messagebox.showwarning(
                        "Knowledge Centre JSON-LD",
                        "Article was created, but the "
                        "BlogPosting JSON-LD section "
                        "could not be found."
                    )

            # -------------------------------------------------
            # SAVE KNOWLEDGE CENTRE
            # -------------------------------------------------

            knowledge_centre_path.write_text(
                knowledge_centre_html,
                encoding="utf-8"
            )

        else:

            messagebox.showwarning(
                "Knowledge Centre",
                "Article was created, but "
                "knowledge-centre.html was not found."
            )

        # -----------------------------------------------------
        # SUCCESS
        # -----------------------------------------------------

        messagebox.showinfo(
            "Success",
            f"Complete mixed-prose article written successfully:\n"
            f"{out_path.name}\n\n"
            f"Knowledge Centre updated successfully."
        )

        self.refresh_articles_list()

    # =========================================================
    # EDIT SESSION
    # =========================================================

    def open_edit_session(self):

        selected_filename = (
            self.edit_file_box.get()
        )

        if (
            not selected_filename
            or "Missing" in selected_filename
        ):

            messagebox.showerror(
                "Error",
                "Please select a verified operational file target first."
            )

            return False

        target_path = (
            KNOWLEDGE_DIR
            / selected_filename
        )

        if self.active_file_path != target_path:

            self.active_file_path = target_path

            self.active_edit_html = (
                target_path.read_text(
                    encoding="utf-8"
                )
            )

            self.edit_log.config(
                state="normal"
            )

            self.edit_log.delete(
                "1.0",
                "end"
            )

            self.edit_log.config(
                state="disabled"
            )

            self.log_message(
                f"--- Session opened for: "
                f"{selected_filename} ---"
            )

        return True

    def ask_for_more_changes(self):

        another_error = messagebox.askyesno(
            "Correction Applied",
            "The correction was applied successfully.\n\n"
            "Are there any other errors you want to correct?"
        )

        if another_error:

            self.edit_typo.focus_set()
            return

        change_image = messagebox.askyesno(
            "Check Images",
            "Do you want to replace or correct any image in this article?"
        )

        if change_image:

            self.edit_old_image.focus_set()
            return

        self.btn_save_edits.focus_set()

    def apply_typo_correction(self):

        if not self.open_edit_session():
            return

        typo = self.edit_typo.get().strip()
        correction = self.edit_correction.get().strip()

        if not typo:

            messagebox.showerror(
                "Error",
                "Text to find cannot be empty."
            )

            return

        if typo == correction:

            messagebox.showwarning(
                "No Change",
                "The old and new text are identical."
            )

            return

        position = self.active_edit_html.find(
            typo
        )

        if position == -1:

            messagebox.showwarning(
                "Not Found",
                f"Specified string pattern "
                f"'{typo}' was not found."
            )

            return

        self.active_edit_html = (
            self.active_edit_html[:position]
            + correction
            + self.active_edit_html[
                position + len(typo):
            ]
        )

        self.log_message(
            f"✅ Replaced ONE occurrence: "
            f"'{typo}' ➔ '{correction}'"
        )

        self.edit_typo.delete(
            0,
            tk.END
        )

        self.edit_correction.delete(
            0,
            tk.END
        )

        self.btn_save_edits.config(
            state="normal"
        )

        self.ask_for_more_changes()

    def browse_image_for_edit(self):

        filename = filedialog.askopenfilename(
            filetypes=[
                (
                    "Image Files",
                    "*.png *.jpg *.jpeg *.webp *.gif"
                )
            ]
        )

        if filename:
            self.edit_new_image.set(
                filename
            )

    def replace_article_image(self):

        if not self.open_edit_session():
            return

        old_image = (
            self.edit_old_image.get().strip()
        )

        new_image = (
            self.edit_new_image.get().strip()
        )

        if not old_image:

            messagebox.showerror(
                "Error",
                "Enter the current image filename, "
                "for example: old-image.jpg"
            )

            return

        if not new_image:

            messagebox.showerror(
                "Error",
                "Please select the replacement image."
            )

            return

        new_image_path = Path(
            new_image
        )

        if not new_image_path.exists():

            messagebox.showerror(
                "Error",
                f"Replacement image was not found:\n"
                f"{new_image_path}"
            )

            return

        IMAGE_DEST_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        new_filename = (
            new_image_path.name
        )

        destination = (
            IMAGE_DEST_DIR
            / new_filename
        )

        shutil.copy2(
            new_image_path,
            destination
        )

        old_filename = Path(
            old_image
        ).name

        old_src = (
            f"../assets/images/{old_filename}"
        )

        new_src = (
            f"../assets/images/{new_filename}"
        )

        occurrences = (
            self.active_edit_html.count(
                old_src
            )
        )

        if occurrences == 0:

            messagebox.showwarning(
                "Image Not Found",
                f"Could not find this image "
                f"reference in the article:\n"
                f"{old_src}"
            )

            return

        self.active_edit_html = (
            self.active_edit_html.replace(
                old_src,
                new_src
            )
        )

        self.log_message(
            f"🖼 Replaced image "
            f"({occurrences} occurrence(s)): "
            f"'{old_filename}' ➔ '{new_filename}'"
        )

        self.edit_old_image.delete(
            0,
            tk.END
        )

        self.edit_new_image.set("")

        self.btn_save_edits.config(
            state="normal"
        )

        another_error = messagebox.askyesno(
            "Image Updated",
            "The image was replaced successfully.\n\n"
            "Are there any other errors or images you want to change?"
        )

        if another_error:

            self.edit_typo.focus_set()

        else:

            self.btn_save_edits.focus_set()

    def save_final_edits(self):

        if (
            self.active_file_path
            and self.active_edit_html
        ):

            self.active_file_path.write_text(
                self.active_edit_html,
                encoding="utf-8"
            )

            messagebox.showinfo(
                "Saved",
                f"All mutations finalized successfully:\n"
                f"{self.active_file_path.name}"
            )

            self.btn_save_edits.config(
                state="disabled"
            )

            self.active_file_path = None
            self.active_edit_html = ""

    # =========================================================
    # GIT
    # =========================================================

    # def trigger_git_engine(self):

    #     msg = (
    #         self.git_commit_msg.get().strip()
    #     )

    #     if not msg:

    #         messagebox.showerror(
    #             "Error",
    #             "Git message cannot be empty."
    #         )

    #         return

    #     confirm = messagebox.askyesno(
    #         "Confirm Commit",
    #         "Execute branch synchronization index pushes now?"
    #     )

    #     if confirm:

    #         try:

    #             os.chdir(REPO_ROOT)

    #             os.system("git add .")

    #             os.system(
    #                 f'git commit -m "{msg}"'
    #             )

    #             os.system("git push")

    #             messagebox.showinfo(
    #                 "Git Push Complete",
    #                 "Repository branch synchronization completed successfully."
    #             )

    #         except Exception as e:

    #             messagebox.showerror(
    #                 "Deployment Failure",
    #                 f"Operation failed:\n{e}"
    #             )
    def trigger_git_engine(self):

        msg = self.git_commit_msg.get().strip()

        if not msg:

            messagebox.showerror(
                "Error",
                "Git commit message cannot be empty."
            )

            return

        confirm = messagebox.askyesno(
            "Publish to Website",
            "Publish all current website changes to GitHub?\n\n"
            "This will:\n"
            "• Stage all changes\n"
            "• Create a Git commit\n"
            "• Push the commit to GitHub\n\n"
            "Vercel will then deploy the updated website."
        )

        if not confirm:
            return

        try:

            import subprocess

            # -------------------------------------------------
            # 1. STAGE ALL CHANGES
            # -------------------------------------------------

            add_result = subprocess.run(
                ["git", "add", "."],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True
            )

            if add_result.returncode != 0:

                raise Exception(
                    add_result.stderr.strip()
                    or "git add failed."
                )

            # -------------------------------------------------
            # 2. CHECK WHETHER THERE ARE CHANGES
            # -------------------------------------------------

            status_result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=REPO_ROOT
            )

            # returncode 0 = no staged changes
            # returncode 1 = staged changes exist

            if status_result.returncode == 0:

                messagebox.showinfo(
                    "No Changes",
                    "There are no changes to publish."
                )

                return

            # -------------------------------------------------
            # 3. CREATE GIT COMMIT
            # -------------------------------------------------

            commit_result = subprocess.run(
                ["git", "commit", "-m", msg],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True
            )

            if commit_result.returncode != 0:

                raise Exception(
                    commit_result.stderr.strip()
                    or commit_result.stdout.strip()
                    or "git commit failed."
                )

            # -------------------------------------------------
            # 4. PUSH TO GITHUB
            # -------------------------------------------------

            push_result = subprocess.run(
                ["git", "push"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True
            )

            if push_result.returncode != 0:

                raise Exception(
                    push_result.stderr.strip()
                    or push_result.stdout.strip()
                    or "git push failed."
                )

            # -------------------------------------------------
            # 5. SUCCESS
            # -------------------------------------------------

            messagebox.showinfo(
                "Published Successfully",
                "Website changes were successfully pushed to GitHub.\n\n"
                "Vercel will automatically deploy the updated website."
            )

        except Exception as e:

            messagebox.showerror(
                "Publishing Failed",
                "The website could not be published.\n\n"
                f"{e}"
            )

# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ArcubusAdminApp(root)

    root.mainloop()