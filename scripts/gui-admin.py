#!/usr/bin/env python3
"""
Arcubus Desktop Admin Dashboard

Features:
- Create new knowledge articles
- Mixed article storyboard:
    * Paragraphs
    * H2 subheadings
    * Images
- Image layout preview:
    * Centre
    * Left
    * Right
- Edit existing articles
- Replace article images
- Manage Our People
- Git publish/deployment
"""

import sys
import os
import shutil
import re
import json
import tempfile
import subprocess
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
# OPTIONAL PILLOW SUPPORT
# =========================================================

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# =========================================================
# PATH SETUP
# =========================================================

if getattr(sys, "frozen", False):
    REPO_ROOT = Path(sys.executable).resolve().parent  # used to find the absolute directory
else:
    REPO_ROOT = Path(__file__).resolve().parent.parent

SITE_DIR = REPO_ROOT / "site"
KNOWLEDGE_DIR = SITE_DIR / "knowledge"
IMAGE_DEST_DIR = SITE_DIR / "assets" / "images"
ARTICLE_TEMPLATE = KNOWLEDGE_DIR / "_TEMPLATE-article.html"
KNOWLEDGE_CENTRE_PATH = SITE_DIR / "knowledge-centre.html"


# =========================================================
# HELPERS
# =========================================================

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text) #Transfer Pricing ->
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


class ArcubusAdminApp:

    def __init__(self, root): # self->instance
        self.root = root
        self.root.title("Arcubus – Website Content Manager Pro")
        self.root.geometry("700x450")
        self.root.minsize(700, 450)

        self.style = ttk.Style()
        self.style.theme_use("vista" if os.name == "nt" else "clam")

        self.storyboard_items = []
        self.pending_images_to_delete = []

        main_frame = ttk.Frame(self.root)
        main_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(5, 0)
        )

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        self.build_article_tab()
        self.build_edit_tab()
        self.build_delete_article_tab()
        self.build_people_tab()
        self.build_git_panel()

    # =========================================================
    # TAB 1: CREATE NEW KNOWLEDGE ARTICLE
    # =========================================================

    def build_article_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" 📝 Create New Article ")

        canvas = tk.Canvas(
            tab, #canvas->child of article tab
            borderwidth=0,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            tab,
            orient="vertical",
            command=canvas.yview
        )

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind( #automatically update the scrolling area
            "<Configure>", # a generated event when the screen's size position changes
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        self.canvas_window = canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(
                self.canvas_window,
                width=e.width
            )
        )

        canvas.configure(yscrollcommand=scrollbar.set)

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
        self.art_category = tk.StringVar()
        self.art_read_time = tk.StringVar()

        ttk.Label(
            self.scrollable_frame,
            text="Article Metadata",
            font=("Segoe UI", 12, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(10, 5),
            padx=5
        )

        ttk.Label(
            self.scrollable_frame,
            text="Article Title / Headline:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=5,
            padx=5
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
            pady=5,
            padx=5
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
            pady=5,
            padx=5
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
            pady=5,
            padx=5
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
            "Selecting the right transfer pricing method for "
            "intra-group services is critical to achieving an "
            "arm’s-length outcome."
        )

        ttk.Label(
            self.scrollable_frame,
            text="Meta Description:"
        ).grid(
            row=5,
            column=0,
            sticky="nw",
            pady=5,
            padx=5
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
            pady=5,
            padx=5
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
            "Key point one.\n"
            "Key point two.\n"
            "Key point three."
        )

        ttk.Separator(
            self.scrollable_frame,
            orient="horizontal"
        ).grid(
            row=7,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=15,
            padx=5
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
            pady=5,
            padx=5
        )

        control_deck = ttk.Frame( # control deck is used to position the 3 buttons
            self.scrollable_frame
        )

        control_deck.grid(
            row=9,
            column=0,
            columnspan=3,
            sticky="w",
            pady=10,
            padx=5
        )

        ttk.Button(
            control_deck,
            text="➕ Add Paragraph",
            command=self.add_paragraph_block
        ).pack(side="left", padx=5)

        ttk.Button(
            control_deck,
            text="➕ Add Subheading (H2)",
            command=self.add_heading_block
        ).pack(side="left", padx=5)

        ttk.Button(
            control_deck,
            text="➕ Add Image Asset",
            command=self.add_image_block
        ).pack(side="left", padx=5)

        self.storyboard_container = ttk.Frame( # for containing all the main body blocks
            self.scrollable_frame
        )

        self.storyboard_container.grid(
            row=10,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=5,
            padx=5
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
            pady=15,
            padx=5
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
            pady=5,
            padx=5
        )

        ttk.Label(
            self.scrollable_frame,
            text="FAQ Question 1:"
        ).grid(
            row=13,
            column=0,
            sticky="w",
            pady=5,
            padx=5
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
            pady=5,
            padx=5
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
            pady=5,
            padx=5
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
            pady=5,
            padx=5
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

        txt_box.pack( #position inside the container
            side="left",
            padx=10,
            pady=10
        )

        item_data = { #dictionary to keep track of dynamically added components
            "type": "p",
            "widget": txt_box,
            "frame": row_frame
        }

        ttk.Button( #lambda function waits for the user to interact with the button before execution
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
            self.storyboard_container, #parent block
            text=" Image Layout Asset Block "
        )

        row_frame.pack(
            fill="x",
            expand=True,
            pady=7
        )

        content_frame = ttk.Frame(row_frame) # frame inside row frame

        content_frame.pack(
            fill="x",
            expand=True,
            padx=8,
            pady=8
        )

        controls_frame = ttk.Frame(content_frame) # for browse function

        controls_frame.grid(
            row=0,
            column=0,
            sticky="nw",
            padx=(2, 15)
        )

        preview_outer = ttk.Frame(content_frame) # for preview

        preview_outer.grid(
            row=0,
            column=1,
            sticky="ne"
        )

        content_frame.columnconfigure(
            0,
            weight=1
        )

        content_frame.columnconfigure(
            1,
            weight=0
        )

        path_var = tk.StringVar()

        path_frame = ttk.Frame(
            controls_frame # parent
        )

        path_frame.pack(
            fill="x",
            pady=(0, 10) # 0 padding abobe and 10 units below
        )

        ttk.Label(
            path_frame,
            text="File Path:"
        ).pack(side="left")

        path_entry = ttk.Entry(
            path_frame,
            textvariable=path_var,
            width=43
        )

        path_entry.pack(
            side="left",
            padx=5
        )

        ttk.Button(
            path_frame,
            text="Browse...",
            command=lambda: self.browse_file(path_var) # again waits till the user clicks the button
        ).pack(side="left")

        position_frame = ttk.LabelFrame(
            controls_frame,
            text=" Image Position "
        )

        position_frame.pack(
            fill="x",
            pady=5
        )

        align_var = tk.StringVar(
            value="c"
        )

        ttk.Radiobutton(
            position_frame,
            text="Centre",
            variable=align_var,
            value="c"
        ).pack(
            side="left",
            padx=12,
            pady=8
        )

        ttk.Radiobutton(
            position_frame,
            text="Left",
            variable=align_var,
            value="l"
        ).pack(
            side="left",
            padx=12,
            pady=8
        )

        ttk.Radiobutton(
            position_frame,
            text="Right",
            variable=align_var,
            value="r"
        ).pack(
            side="left",
            padx=12,
            pady=8
        )

        item_data = {
            "type": "i",
            "path": path_var,
            "align": align_var,
            "frame": row_frame # stores outer container so that the block can be removed
        }

        preview_canvas = self.create_image_preview( #calls method that was initilialised in init
            preview_outer,
            path_var,
            align_var
        )

        item_data["preview_canvas"] = preview_canvas

        def on_path_change(*args):
            self.update_image_preview(
                preview_canvas,
                path_var,
                align_var
            )

        path_var.trace_add( #once user selects an image or changes the path the preview changes
            "write",
            on_path_change
        )

        def on_alignment_change(*args):
            self.update_image_preview(
                preview_canvas,
                path_var,
                align_var
            )

        align_var.trace_add( #changes the preview if centreleft,right changes
            "write",
            on_alignment_change
        )

        button_frame = ttk.Frame(row_frame)

        button_frame.pack(
            fill="x",
            padx=8,
            pady=(0, 8)
        )

        ttk.Button(
            button_frame,
            text="❌ Remove",
            command=lambda: self.remove_storyboard_item(
                row_frame,
                item_data
            )
        ).pack(
            side="right"
        )

        self.storyboard_items.append(
            item_data
        )

        self.update_image_preview(
            preview_canvas,
            path_var,
            align_var
        )

    def create_image_preview(
        self,
        parent, #preview-outer
        path_var,
        align_var
    ):
        preview_frame = ttk.LabelFrame(
            parent,
            text=" Live Article Preview "
        )

        preview_frame.pack(
            anchor="ne"
        )

        preview_canvas = tk.Canvas(
            preview_frame,
            width=430,
            height=235,
            background="white",
            highlightbackground="#c8c8c8",
            highlightthickness=1
        )

        preview_canvas.pack(
            padx=8,
            pady=8
        )

        preview_canvas.preview_photo = None

        return preview_canvas

    def update_image_preview(
        self,
        canvas,
        path_var,
        align_var
    ):
        if not canvas.winfo_exists():
            return

        canvas.delete("all")

        canvas_width = 430
        canvas_height = 235

        left = 18
        top = 16
        right = canvas_width - 18
        bottom = canvas_height - 16

        canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill="#ffffff",
            outline="#dddddd"
        )

        align = align_var.get() # stores the current algnment stored (c,l,r)

        image_path = path_var.get().strip()

        loaded_image = None

        if image_path:# checks if contains a non empty string
            try:
                image_path_obj = Path(image_path) # converts into a path object

                if image_path_obj.exists():
                    if PIL_AVAILABLE:
                        loaded_image = Image.open(
                            image_path_obj
                        )

                        loaded_image.thumbnail(
                            (105, 80),
                            Image.LANCZOS
                        )

                        canvas.preview_photo = ImageTk.PhotoImage(
                            loaded_image.copy()
                        )

            except Exception:
                loaded_image = None
        else:
            canvas.preview_photo = None

        image_width = 105
        image_height = 80

        image_x = 0
        image_y = 0

        if align == "c":

            self.draw_preview_text_lines(
                canvas,
                40,
                32,
                350,
                3
            )

            image_x = (
                canvas_width // 2
                - image_width // 2
            )

            image_y = 82

            self.draw_preview_image(
                canvas,
                image_x,
                image_y,
                image_width,
                image_height,
                loaded_image
            )

            self.draw_preview_text_lines(
                canvas,
                45,
                178,
                340,
                2
            )

            canvas.create_text(
                canvas_width // 2,
                218,
                text="Centre — image sits between text",
                fill="#777777",
                font=("Segoe UI", 9)
            )

        elif align == "l":

            image_x = 32
            image_y = 58

            self.draw_preview_image(
                canvas,
                image_x,
                image_y,
                image_width,
                image_height,
                loaded_image
            )

            self.draw_preview_text_lines(
                canvas,
                155,
                38,
                225,
                7
            )

            self.draw_preview_text_lines(
                canvas,
                35,
                153,
                360,
                2
            )

            canvas.create_text(
                canvas_width // 2,
                218,
                text="Left — text wraps around the right side",
                fill="#777777",
                font=("Segoe UI", 9)
            )

        elif align == "r":

            image_x = (
                canvas_width
                - image_width
                - 32
            )

            image_y = 58

            self.draw_preview_image(
                canvas,
                image_x,
                image_y,
                image_width,
                image_height,
                loaded_image
            )

            self.draw_preview_text_lines(
                canvas,
                35,
                38,
                225,
                7
            )

            self.draw_preview_text_lines(
                canvas,
                35,
                153,
                360,
                2
            )

            canvas.create_text(
                canvas_width // 2,
                218,
                text="Right — text wraps around the left side",
                fill="#777777",
                font=("Segoe UI", 9)
            )

    def draw_preview_image(
        self,
        canvas,
        x,
        y,
        width,
        height,
        loaded_image
    ):
        if loaded_image is not None:
            canvas.create_image(
                x + width // 2,
                y + height // 2,
                image=canvas.preview_photo
            )

            canvas.create_rectangle(
                x,
                y,
                x + width,
                y + height,
                outline="#999999"
            )

            return

        canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill="#eeeeee",
            outline="#aaaaaa"
        )

        canvas.create_polygon(
            x + 20,
            y + height - 18,
            x + 48,
            y + 35,
            x + 68,
            y + 55,
            x + 86,
            y + 27,
            x + width - 18,
            y + height - 18,
            fill="#bbbbbb",
            outline=""
        )

        canvas.create_oval(
            x + width - 34,
            y + 15,
            x + width - 17,
            y + 32,
            fill="#bbbbbb",
            outline=""
        )

        canvas.create_text(
            x + width // 2,
            y + height // 2 + 10,
            text="IMAGE",
            fill="#777777",
            font=("Segoe UI", 9, "bold")
        )

    def draw_preview_text_lines(
        self,
        canvas,
        x,
        y,
        width,
        count
    ):
        line_height = 12

        widths = [
            0.96,
            0.84,
            0.91,
            0.76,
            0.88,
            0.80,
            0.67,
            0.94
        ]

        for i in range(count):
            fraction = widths[
                i % len(widths)
            ]

            line_width = width * fraction

            canvas.create_rectangle(
                x,
                y + i * line_height,
                x + line_width,
                y + i * line_height + 5,
                fill="#b8b8b8",
                outline=""
            )

    def remove_storyboard_item(
        self,
        frame,
        item_data
    ):
        frame.destroy()

        if item_data in self.storyboard_items:
            self.storyboard_items.remove(
                item_data
            )

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

        self.edit_file_box = ttk.Combobox( #combobox for dropdown
            tab,
            width=45,
            state="readonly"
        )

        self.edit_file_box.grid( #helps with the positioning of the container
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
        
        
        #addition of new code 
        
        ttk.Button(
            tab,
            text="View Article Images",
            command=self.show_article_images
        ).grid(
            row=7,
            column=2,
            sticky="w",
            padx=5
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

        self.active_edit_html = ""
        self.active_file_path = None

        self.refresh_articles_list()
        
    # =========================================================
    # DELETE ARTICLE TAB
    # =========================================================
    
    def build_delete_article_tab(self):
        tab = ttk.Frame(self.notebook)
        
        self.notebook.add(
            tab,
            text= "🗑️ Delete Article "
        )
        
        ttk.Label(
            tab,
            text="Delete Existing Knowledge Article ",
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
            tab,
            text="Select an Article to remove from the website. "
                 "Knowledge Centre and associated image assets. "
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            padx=15,
            pady=(0, 15)
        )
        
        ttk.Label(
            tab,
            text="Select Article ",
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=15,
            pady=10
        )
        
        self.delete_article_box = ttk.Combobox(
            tab,
            width=45,
            state="readonly"
        )
        
        self.delete_article_box.grid(
            row=2,
            column=1,
            sticky="w",
            padx=5,
            pady=8
        )
        
        ttk.Button(
            tab,
            text="🔄 Refresh",
            command=self.refresh_delete_articles_list
        ).grid(
            row=2,
            column=2,
            sticky="w",
            padx=5,
            pady=8
        )
        
        ttk.Label(
            tab,
            text=(
                "Warning: deletion changes your local website files. "
                "Publish your changes separately to update the live website."
            ),
            wraplength=600
        ).grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="w",
            padx=15,
            pady=15
        )
        
        ttk.Button(
            tab,
            text="🗑️ Delete Selected Article",
            command=self.delete_selected_article
        ).grid(
            row=4,
            column=1,
            sticky="w",
            padx=5,
            pady=10
        )
        
        self.refresh_delete_articles_list()
        
    def refresh_delete_articles_list(self):
        """Refresh the dropdown with existing articles."""
        
        if not KNOWLEDGE_DIR.exists(): #if knowledge centre page doesnt exist the dropdown shows 0 values
            self.delete_article_box["values"] = []
            return
        
        files = sorted( #inbuilt pyhton function for displaying articles in alphabetical order
            path.name
            for path in KNOWLEDGE_DIR.glob("*.html") #glob searches for the matching filename
            if not path.name.startswith("_") # reason know-centre template has _ so for no confusion
        )
        
        self.delete_article_box["values"] = files #current dropdown articles are stored in list

        if files:
            current = self.delete_article_box.get()

            if current in files:
                self.delete_article_box.set(current)# if selected article is in list delete it
            else:
                self.delete_article_box.current(0)# if selection is invalid then upon refreshing the code selects the first item in the list
        else:
            self.delete_article_box.set("")# if no files present
            
            
    # =========================================================
    # DELETE ARTICLE LOGIC
    # =========================================================

    def delete_selected_article(self):
        """
        Delete the selected article, update the Knowledge Centre,
        and remove associated images when they are not shared
        with other website pages.
        """
        
        #select the file from dropdown
        selected_filename = self.delete_article_box.get().strip()

        if not selected_filename:
            messagebox.showerror(
                "No Article Selected",
                "Please select an article to delete."
            )
            return

        # Only allow a filename, not an arbitrary filesystem path.
        if (
            Path(selected_filename).name != selected_filename#cms should delete articles from the cmd not any random plcae 
            or not selected_filename.endswith(".html")
            or selected_filename.startswith("_")
        ):
            messagebox.showerror(
                "Invalid Selection",
                "The selected article filename is invalid."
            )
            return

        article_path = KNOWLEDGE_DIR / selected_filename #construct the file path

        # Resolve the path and verify that it stays inside
        # the knowledge directory.
        try:
            article_path = article_path.resolve()
            knowledge_root = KNOWLEDGE_DIR.resolve()

            if (
                article_path.parent != knowledge_root #checks if articles parent==know dir
                or not article_path.is_file()
            ):
                messagebox.showerror(
                    "Article Not Found",
                    "The selected article file does not exist."
                )
                return

        except OSError as e:
            messagebox.showerror(
                "Path Error",
                f"Could not validate the article path:\n{e}"
            )
            return

        # -----------------------------------------------------
        # STEP 3: CHECK THE KNOWLEDGE CENTRE
        # -----------------------------------------------------
        
        #is_file checks whether the path is true and also if it is an actual file(not a folder)(returns yes when both true)
        
        if not KNOWLEDGE_CENTRE_PATH.is_file():
            messagebox.showerror(
                "Knowledge Centre Error",
                "knowledge-centre.html was not found.\n\n"
                "The article has not been deleted."
            )
            return

        # -----------------------------------------------------
        # STEP 4: READ THE ARTICLE AND KNOWLEDGE CENTRE
        # -----------------------------------------------------

        try:
            article_html = article_path.read_text( #standalone file
                encoding="utf-8" #read for figuring out the images
            )

            knowledge_html = KNOWLEDGE_CENTRE_PATH.read_text(
                encoding="utf-8"#for finding the entry of the article in know-centre page
            )

        except (OSError, UnicodeError) as e:
            messagebox.showerror(
                "Read Error",
                f"Could not read the required HTML files:\n{e}"
            )
            return

        # The standalone file is named <slug>.html.
        # Therefore, its stem is the article slug.
        #slug = article_path.stem#.stem returns file name without extension

        article_url = f"knowledge/{selected_filename}"

        # -----------------------------------------------------
        # STEP 5: FIND LOCAL ARTICLE IMAGES
        # -----------------------------------------------------

        image_pattern = (
            r"""(?:src)\s*=\s*["']([^"']+)["']"""
        ) # stores the regex string in image_pattern

        image_references = re.findall(#extracts all image references
            image_pattern,
            article_html, #defined in above section
            flags=re.IGNORECASE#makes matching case insensetive
        )

        article_images = set()#python built in function for creating set

        for reference in image_references:

            # Ignore query strings and URL fragments.
            reference = reference.split("#", 1)[0]
            reference = reference.split("?", 1)[0]
            #for splitting browser urls

            # Ignore remote URLs, embedded images, and unrelated
            # assets. The article creator uses this exact path.
            if not reference.startswith("../assets/images/"):
                continue
            #as we need to delete the images from assets folder as well

            image_filename = Path(reference).name
            #if ref = "../assets/images/transfer-pricing.jpg" ; Path(reference).name= transfer-pricing.jpg
            #done to locate the img in the assets folder properly

            if not image_filename:
                continue

            image_path = (
                IMAGE_DEST_DIR / image_filename
            ).resolve()

            # Only allow files directly inside assets/images.
            try:
                if image_path.parent != IMAGE_DEST_DIR.resolve():#cross-checks whether the img is inside the assets folder
                    continue
            except OSError:
                continue

            if image_path.is_file():
                article_images.add(image_path)#the set was created at the beginning of the section

        # -----------------------------------------------------
        # STEP 6: PREPARE THE UPDATED KNOWLEDGE CENTRE
        # -----------------------------------------------------
        #responsible finding and removing a particular article's card from knowledge-centre.html
        
        card_pattern = re.compile(# searches for an anchor tag
            r'<a\b'#matches HTML tag opening with a; \b regex word boundary
            r'(?=[^>]*\bhref\s*=\s*["\']'
            + re.escape(article_url)
            + r'["\'])'
            r'[^>]*>.*?</a>',
            flags=re.IGNORECASE | re.DOTALL#makes it case insestive
        )
        
        #subn returns 2 values in tuple
        #updated_knowledge_html#this variable recieves modified HTML; cards_removed = #receives no.of substitutions
        updated_knowledge_html, cards_removed = (
            card_pattern.subn(
                "",#matching string is replaced with nothing
                knowledge_html#source string
            )
        )

        if cards_removed == 0:
            messagebox.showerror(
                "Article Card Not Found",
                "The selected article was not found in "
                "knowledge-centre.html.\n\n"
                "No files have been deleted. Please check "
                "the Knowledge Centre entry manually."
            )
            return

        
        #remove standalone file
        target_url = f"arcubus.in/knowledge/{selected_filename}"

        url_position = updated_knowledge_html.find(target_url)#returns the starting index of url

        if url_position != -1:

            # Find the opening brace of the BlogPosting object.
            object_start = updated_knowledge_html.rfind(
                "{",# rfind finds the last occurence of "{"
                0, #index of search range beginning
                url_position
            )

            if object_start != -1:

                depth = 0 # keeps track of nesting level of the 
                in_string = False #tracks whether the current character being read is inside a JSON string or outside it
                #escaped_char = False
                object_end = None #initially none as the end hasnt been found

                # Find the matching closing brace, ignoring
                # braces that occur inside JSON strings.

                for index in range(
                    object_start,
                    len(updated_knowledge_html)
                ):

                    char = updated_knowledge_html[index]

                    if in_string:

                        # if escaped_char:
                        #     escaped_char = False

                        # elif char == "\\":
                        #     escaped_char = True

                        elif char == '"':
                            in_string = False

                        continue

                    if char == '"':
                        in_string = True

                    elif char == "{":
                        depth += 1

                    elif char == "}":
                        depth -= 1

                        if depth == 0:
                            object_end = index + 1
                            break

                if object_end is not None:

                    # Remove the object and one adjacent comma,
                    # if present, so the JSON array remains valid.

                    remove_start = object_start
                    remove_end = object_end

                    #slicing
                    before = updated_knowledge_html[:remove_start]
                    after = updated_knowledge_html[remove_end:]

                    if before.rstrip().endswith(","):
                        comma_position = (
                            len(before.rstrip()) - 1
                        )
                        remove_start = comma_position

                    elif after.lstrip().startswith(","):
                        comma_position = ( #finds loc in the original html string
                            remove_end
                            + len(after) - len(after.lstrip())
                        )
                        remove_end = comma_position + 1

                    updated_knowledge_html = (
                        updated_knowledge_html[:remove_start]
                        + updated_knowledge_html[remove_end:]
                    )

        # -----------------------------------------------------
        # STEP 8: CONFIRM BEFORE DELETION
        # -----------------------------------------------------

        image_names = sorted(
            image.name for image in article_images
        )

        image_summary = (
            "\n\nImages referenced by this article:\n"
            + "\n".join(image_names)
            if image_names
            else "\n\nNo local article images were found."
        )

        confirmed = messagebox.askyesno(
            "Confirm Article Deletion",
            f"Are you sure you want to delete "
            f"'{selected_filename}'?\n\n"
            "The following changes will be made:\n"
            "• Delete the standalone article HTML file.\n"
            "• Remove its Knowledge Centre card.\n"
            "• Remove its BlogPosting structured-data entry."
            + image_summary
            + "\n\nImages used elsewhere on the website "
              "will be preserved.\n\n"
              "This action cannot be undone automatically."
        )

        if not confirmed:
            return

        # -----------------------------------------------------
        # STEP 9: WRITE THE UPDATED KNOWLEDGE CENTRE
        # -----------------------------------------------------

        # Prepare the updated HTML before deleting the article.
        # A backup allows the Knowledge Centre to be restored
        # if a later filesystem operation fails.

        backup_path = None
        deleted_images = []
        article_deleted = False

        try:

            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                suffix=".html",
                prefix="knowledge-centre-backup-",
                dir=KNOWLEDGE_CENTRE_PATH.parent,
                delete=False
            ) as backup_file:

                backup_file.write(knowledge_html)
                backup_path = Path(backup_file.name)

            KNOWLEDGE_CENTRE_PATH.write_text(
                updated_knowledge_html,
                encoding="utf-8"
            )

            # -------------------------------------------------
            # STEP 10: DELETE THE STANDALONE ARTICLE
            # -------------------------------------------------

            article_path.unlink()
            article_deleted = True

            # -------------------------------------------------
            # STEP 11: DELETE ARTICLE IMAGES
            # -------------------------------------------------

            for image_path in sorted(article_images):
                if image_path.is_file():
                    image_path.unlink()
                    deleted_images.append(image_path.name)
        
        
        except OSError as e:
            messagebox.showerror(
                "Deletion Error",
                f"An error occurred while deleting the article:\n{e}"
            )
            return    

        # -----------------------------------------------------
        # STEP 12: REMOVE TEMPORARY BACKUP
        # -----------------------------------------------------

        if backup_path:
            try:
                backup_path.unlink(missing_ok=True)
            except OSError:
                pass

        # -----------------------------------------------------
        # STEP 13: UPDATE THE GIT COMMIT MESSAGE
        # -----------------------------------------------------

        self.update_git_commit_message(
            "Article deleted from Knowledge Centre"
        )

        # -----------------------------------------------------
        # STEP 14: REFRESH THE DROPDOWN
        # -----------------------------------------------------

        self.refresh_delete_articles_list()

        # Also refresh the Edit Article dropdown if it exists.
        self.refresh_articles_list()

        # -----------------------------------------------------
        # STEP 15: SHOW SUCCESS MESSAGE
        # -----------------------------------------------------

        shared_images = (
            len(article_images) - len(deleted_images)
        )

        message = (
            f"Article deleted successfully!\n\n"
            f"Article: {selected_filename}\n"
            f"Knowledge Centre: Updated\n"
            f"BlogPosting structured data: Checked\n"
            f"Images deleted: {len(deleted_images)}\n"
            f"Images preserved because they are shared: "
            f"{max(0, shared_images)}\n\n"
            "Publish your changes separately to update "
            "the live website."
        )

        messagebox.showinfo(
            "Article Deleted",
            message
        )

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
            text="Add, edit, delete and replace profile images "
                 "without manually editing our-people.html."
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
            self.person_expertise2
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

        self.person_default_image.set(
            False
        )

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

        self.person_name.delete(
            0,
            tk.END
        )

        self.person_name.insert(
            0,
            person["name"]
        )

        self.person_role.delete(
            0,
            tk.END
        )

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

        self.person_default_image.set(
            False
        )

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
            self.person_new_image.set(
                filename
            )

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
            self.add_person_image.set(
                filename
            )

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
                use_default_image=self.person_default_image.get()
            )

            messagebox.showinfo(
                "Updated",
                "Person updated successfully.\n\n"
                "our-people.html was updated.\n"
                f"Backup created:\n{backup.name}"
            )

            self.refresh_people_list()
            
            
            self.update_git_commit_message(
                "Our People section updated"
            )

        except PeopleManagerError as e:
            messagebox.showerror(
                "Update Failed",
                str(e)
            )

    def add_new_person(self):
        name = self.add_person_name.get().strip()
        role = self.add_person_role.get().strip()

        bio = self.add_person_bio.get(
            "1.0", # read from line 1 character 0
            "end"  # read till end
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
                image_path=image_path
            )
            
            

            messagebox.showinfo(
                "Person Added",
                "New person added successfully.\n\n"
                "our-people.html was updated.\n"
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
            
            self.update_git_commit_message(
                "Our People section updated"
        )

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
                "Delete this person from the Our People page?\n\n"
                f"{person['name']} — {person['role']}\n\n"
                "This will remove the visible card and its "
                "Person JSON-LD entry."
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
            
            self.update_git_commit_message(
                "Our People section updated"
            )

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
            pady=(1,1),
        )

        inner = ttk.Frame(panel)

        inner.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=6
        )

        self.git_commit_msg = tk.StringVar(
            value="Content update to the website."
        )

        ttk.Label(
            inner,
            text="Git Commit Message:",
            font=("Segoe UI", 11) # newly added
        ).pack(
            side="left",
            padx=(4, 8)
        )

        ttk.Entry(
            inner,
            textvariable=self.git_commit_msg,
            width=55
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        ttk.Button(
            inner,
            text="🚀 Push Changes to GitHub",
            command=self.trigger_git_engine
        ).pack(
            side="right",
            padx=(20, 4)
        )
        
    
    def update_git_commit_message(self, message):
        self.git_commit_msg.set(message)

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

        desc = self.art_desc.get(
            "1.0",
            "end"
        ).strip()

        if not desc:
            desc = (
                f"{title} — practical guidance from "
                "Arcubus Advisors."
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
            f"{escape(t)}"
            for t in tk_list
        )

        compiled_body_blocks = []

        for item in self.storyboard_items:

            if item["type"] == "p":

                val = item["widget"].get(
                    "1.0",
                    "end"
                ).strip()

                if val:
                    compiled_body_blocks.append(
                        val
                    )

            elif item["type"] == "h":

                val = item["widget"].get().strip()

                if val:
                    compiled_body_blocks.append(
                        val
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

                        compiled_body_blocks.append( # escape needed to prevent broken HTML layout and ensure the webpage renders correctly 
                                                    #you are using Python f-strings to inject variables directly into HTML attributes
                            f'<figure class="{align_class}">'
                            f'<img src="../assets/images/{escape(img_path.name)}" '
                            f'alt="{escape(img_path.stem)}">'
                            f'</figure>'
                        )

                    else:
                        messagebox.showwarning(
                            "Image Not Found",
                            f"The image file could not be found:\n\n"
                            f"{img_str}"
                        )
                        return

        body_text = "\n".join(
            compiled_body_blocks
        ).strip()

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
            title if title.endswith(".")
            else title + "."
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
            "REPLACE — one or two sentences saying what the reader "
            "will be able to do after reading. Keep under 58 characters "
            "per line of measure; the CSS handles the wrapping.",
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
        # FAQ 1
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
                f'"name": "{escape(q1)}"'
            )

            html = html.replace(
                '"text": "REPLACE — answer it directly in the first sentence, then add the qualification."',
                f'"text": "{escape(a1)}"'
            )

        # -----------------------------------------------------
        # FAQ 2
        # -----------------------------------------------------

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
                f'"name": "{escape(q2)}"'
            )

            html = html.replace(
                '"text": "REPLACE — answer."',
                f'"text": "{escape(a2)}"'
            )

        out_path = KNOWLEDGE_DIR / f"{slug}.html"
        
        self.update_git_commit_message(
            "New article created for Knowledge Centre"
        )

        KNOWLEDGE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        out_path.write_text(
            html,
            encoding="utf-8"
        )

        # =====================================================
        # UPDATE KNOWLEDGE CENTRE
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

            display_date = today.strftime(
                "%d %B %Y"
            )

            iso_date = today.strftime(
                "%Y-%m-%d"
            )

            # -------------------------------------------------
            # IMPORTANT:
            # This marker should match the marker present
            # in your knowledge-centre.html.
            # -------------------------------------------------

            
            article_grid_marker = '<div class="grid g3">'
            
            new_article_card = f'''<a class="articlecard" href="knowledge/{slug}.html">
            <span class="tag">{safe_category}</span>
            <h3>{safe_title}</h3>
            <p>{safe_lede}</p>
            <span class="date">{display_date} · {safe_read_time}</span>
            </a>'''


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
                        "Article grid could not be found."
                    )

                new_blog_post = {
                    "@type": "BlogPosting",
                    "headline": title,
                    "url": f"arcubus.in/knowledge/{slug}.html",
                    "datePublished": iso_date,
                    "description": lede,
                    "author": {
                        "@id": "arcubus.in"
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
                        "BlogPosting JSON-LD section not found."
                    )

                knowledge_centre_path.write_text(
                    knowledge_centre_html,
                    encoding="utf-8"
                )

        else:

            messagebox.showwarning(
                "Knowledge Centre",
                "knowledge-centre.html was not found."
            )

        messagebox.showinfo(
            "Success",
            f"Article written successfully:\n"
            f"{out_path.name}\n\n"
            "Knowledge Centre updated."
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
                "Please select a verified operational "
                "file target first."
            )
            return False

        target_path = (
            KNOWLEDGE_DIR
            / selected_filename
        )

        if not target_path.exists():
            messagebox.showerror(
                "Error",
                f"Target article does not exist:\n"
                f"{target_path}"
            )
            return False

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
            "Do you want to replace or correct "
            "any image in this article?"
        )

        if change_image:
            self.edit_old_image.focus_set()
            return

        self.btn_save_edits.focus_set()

    def apply_typo_correction(self):
        if not self.open_edit_session():
            return

        typo = self.edit_typo.get().strip()
        correction = (
            self.edit_correction.get().strip()
        )

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
        
    
    #Addition in the code
    
    def show_article_images(self):

        # Load the selected article into the current edit session.
        if not self.open_edit_session():
            return

        # Find image paths in src and data-src attributes.
        pattern = (
            r"""(?:src|data-src)\s*=\s*["']([^"']+)["']"""
        )

        references = re.findall(
            pattern, #regex mentioned above
            self.active_edit_html, # currently selected html file
            flags=re.IGNORECASE # makes the search case-insensitive
        )

        images = [] #contains the file names for displaying
        seen = set() #keeps a track of already existing filenames

        for reference in references:
            reference = reference.strip() # removes blank spaces in the name if any exists

            # Ignore remote URLs, embedded images and fragments.
            if reference.startswith(
                ("http://", "https://", "//", "data:", "#")
            ):
                continue

            # Match the same folder path used by the existing
            # replace_article_image() function.
            reference = reference.split("?")[0].split("#")[0]
            reference = reference.replace("\\", "/")

            if not reference.startswith("../assets/images/"):
                continue

            filename = Path(reference).name
            extension = Path(filename).suffix.lower()

            if extension not in {
                ".png", ".jpg", ".jpeg", ".webp", ".gif"
            }:
                continue

            if filename not in seen:
                seen.add(filename)
                images.append(filename)

        if not images:
            messagebox.showinfo(
                "No Images Found",
                "No supported local images were found in this article."
            )
            return

        # Create the gallery window.
        window = tk.Toplevel(self.root)
        window.title("Images in Selected Article")
        window.geometry("650x450")
        window.minsize(450, 300)
        window.transient(self.root)

        ttk.Label(
            window,
            text="Select the image you want to replace",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=12, pady=12)

        # Scrollable gallery.
        container = ttk.Frame(window)
        container.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 12)
        )

        canvas = tk.Canvas(container, highlightthickness=0)

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview
        )

        gallery = ttk.Frame(canvas)

        gallery_window = canvas.create_window(
            (0, 0),
            window=gallery,
            anchor="nw"
        )

        gallery.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                gallery_window,
                width=event.width
            )
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Keep thumbnail references alive so Tkinter can display them.
        window.thumbnail_refs = []

        for filename in images:
            image_path = IMAGE_DEST_DIR / filename

            row = ttk.Frame(
                gallery,
                padding=8,
                relief="groove" #gives the row a bordered appearance.
            )
            row.pack(fill="x", pady=4)

            # Show a thumbnail when Pillow is installed.
            if PIL_AVAILABLE and image_path.is_file():
                try:
                    with Image.open(image_path) as source:
                        thumbnail = source.convert("RGB")
                        thumbnail.thumbnail((110, 75))

                        photo = ImageTk.PhotoImage(
                            thumbnail,
                            master=window
                        )

                    window.thumbnail_refs.append(photo)

                    ttk.Label(
                        row,
                        image=photo
                    ).pack(side="left", padx=(0, 12))

                except Exception:
                    pass

            details = ttk.Frame(row)
            details.pack(side="left", fill="x", expand=True)

            ttk.Label(
                details,
                text=filename,
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w")

            if not image_path.is_file():
                ttk.Label(
                    details,
                    text="File not found in assets/images",
                ).pack(anchor="w")

            ttk.Button(
                row,
                text="Select",
                command=lambda name=filename: (
                    self.select_article_image(name, window)
                )
            ).pack(side="right", padx=5)


    def select_article_image(self, filename, window):

        self.edit_old_image.delete(0, tk.END)
        self.edit_old_image.insert(0, filename)

        window.destroy()

        self.log_message(
            f"Selected image for replacement: {filename}"
        )


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
            self.edit_new_image.set( # stores the browsed image's path in input field
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
                "Replacement image was not found:\n"
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

        shutil.copy2( #here the image is coped into assets folder
            new_image_path,
            IMAGE_DEST_DIR / new_filename
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
                "Could not find this image reference:\n"
                f"{old_src}"
            )
            return

        self.active_edit_html = (
            self.active_edit_html.replace(
                old_src,
                new_src
            )
        )
        
        #ADDITION
        old_image_path = IMAGE_DEST_DIR / old_filename
        
        if(
            old_filename != new_filename
            and old_image_path.exists()
        ):
            self.pending_images_to_delete.append(
                old_image_path
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
            "Are there any other modifications?"
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
            try:
                # 1. Save the updated HTML first
                self.active_file_path.write_text(
                    self.active_edit_html,
                    encoding="utf-8"
                )

            except OSError as e:
                messagebox.showerror(
                    "Save Failed",
                    f"Could not save the article:\n{e}\n\n"
                    "The old images have not been deleted."
                )
                return

        # 2. Delete old images only after HTML saves
            for image_path in self.pending_images_to_delete:
                try:
                    if image_path.exists():
                        image_path.unlink()

                        self.log_message(
                            f"Deleted old image: {image_path.name}"
                        )

                except OSError as e:
                    self.log_message(
                        f"Could not delete old image "
                        f"{image_path.name}: {e}"
                    )

            # 3. Clear the pending-deletion list
            self.pending_images_to_delete.clear()

            # 4. Confirm successful save
            messagebox.showinfo(
                "Saved",
                "All changes saved successfully:\n"
                f"{self.active_file_path.name}"
            )
            
            self.update_git_commit_message(
            "Content update to Knowledge Centre articles"
        )

            self.btn_save_edits.config(
                state="disabled"
            )

            self.active_file_path = None
            self.active_edit_html = ""
    

    def trigger_git_engine(self):
        msg = (
            self.git_commit_msg.get().strip()
        )

        if not msg:
            messagebox.showerror(
                "Error",
                "Git commit message cannot be empty."
            )
            return

        confirm = messagebox.askyesno(
            "Publish to Website",
            "Publish all current website changes to GitHub?\n\n"
            "This will stage, commit, and push updates "
            "to trigger Vercel deployment."
        )

        if not confirm:
            return
        
        #credentials = self.ask_github_credentials()
        
        # if not credentials:
        #     return
        
        # ADDITION Explicitly declare tracking states for the security restoration block
        # original_url = None
        # url_modified = False

        try:
            import subprocess
            git_repo = SITE_DIR
            
            # -------------------------------------------------
            # 1. STAGE CHANGES
            # -------------------------------------------------

            add_result = subprocess.run(
                ["git", "add", "."],
                cwd=git_repo,
                capture_output=True,
                text=True
            )

            if add_result.returncode != 0:
                raise Exception(
                    add_result.stderr.strip()
                    or "git add failed."
                )

            # -------------------------------------------------
            # 2. CHECK FOR STAGED CHANGES
            # -------------------------------------------------

            status_result = subprocess.run(
                [
                    "git",
                    "diff",
                    "--cached",
                    "--quiet"
                ],
                cwd=git_repo
            )

            if status_result.returncode == 0:
                messagebox.showinfo(
                    "No Changes",
                    "There are no changes to publish."
                )
                return

            # -------------------------------------------------
            # 3. COMMIT
            # -------------------------------------------------

            commit_result = subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    msg
                ],
                cwd=git_repo,
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
            # 4. PUSH
            # -------------------------------------------------
            
            
            push_result = subprocess.run(
                ["git", "push"],
                cwd=git_repo,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode != 0:
                raise Exception(
                    push_result.stderr.strip()
                    or push_result.stdout.strip()
                    or "git push failed."
                )

            messagebox.showinfo(
                "Published Successfully",
                "Website changes were successfully "
                "pushed to GitHub.\n\n"
                "Vercel will automatically deploy "
                "the updated website."
            )

        except Exception as e:

            messagebox.showerror(
                "Publishing Failed",
                "The website could not be published.\n\n"
                f"{e}"
            )

# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = ArcubusAdminApp(root)
    root.mainloop()