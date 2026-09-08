# import streamlit as st
# import os
# import datetime

# # Set up paths inside your 'site' directory based on your terminal layout
# SITE_DIR = "site"
# KNOWLEDGE_DIR = os.path.join(SITE_DIR, "knowledge")
# IMAGES_DIR = os.path.join(SITE_DIR, "images")

# # Ensure these directories exist
# os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
# os.makedirs(IMAGES_DIR, exist_ok=True)

# # Page Configuration
# st.set_page_config(page_title="Arcubus Publisher Pro", page_icon="📝", layout="wide")

# st.title("📰 Arcubus Knowledge Center Publisher")
# st.write("Fill out the metadata and content below to instantly publish a formatted HTML article.")

# # Use columns to split Metadata and Main Content for a cleaner layout
# col1, col2 = st.columns([1, 1], gap="large")

# with col1:
#     st.subheader("1. Article Metadata")
    
#     title = st.text_input("1. Article Title (Headline)", placeholder="How to choose the right transfer pricing method...")
    
#     # Auto-generate a fallback slug if the user leaves it blank
#     default_slug = "".join(c for c in title.lower() if c.isalnum() or c in " ").replace(" ", "-")
#     slug = st.text_input("2. Filename / Slug (without .html)", placeholder="choosing-transfer-pricing-method-intra-group-services", value=default_slug)
    
#     category = st.text_input("3. Category", placeholder="Transfer Pricing Methods, Benchmarking, etc.")
    
#     publish_date = st.date_input("4. Publish Date", value=datetime.date.today())
    
#     meta_desc = st.text_area("5. Meta Description (150-160 chars)", max_chars=160, placeholder="A practical guide to selecting the most appropriate transfer pricing method...")
    
#     read_time = st.text_input("6. Estimated Read Time", placeholder="e.g., 6 min")

#     st.subheader("2. Key Takeaways (One per line)")
#     takeaways_input = st.text_area("7. Enter 3–5 points:", height=150, placeholder="Point 1\nPoint 2\nPoint 3")

# with col2:
#     st.subheader("3. Image & Visuals")
#     uploaded_file = st.file_uploader("Upload Article Image", type=["png", "jpg", "jpeg", "webp"])
    
#     alignment = st.radio(
#         "Image Alignment",
#         ["Left (Text wraps around the right side)", "Center (Image is on its own line)", "Right (Text wraps around the left side)"],
#         index=0
#     )

#     st.subheader("4. Article Body")
#     content = st.text_area("8. Main Body Content (HTML tags are supported)", height=250, placeholder="Paste everything that should go inside the article body here...")

#     st.subheader("5. Frequently Asked Questions (Optional)")
    
#     # Simple dynamic block for up to 3 FAQ entries
#     faq_data = []
#     for i in range(1, 4):
#         q = st.text_input(f"Question {i}:", key=f"q_{i}", placeholder=f"FAQ Question {i}")
#         a = st.text_area(f"Answer {i}:", key=f"a_{i}", height=70, placeholder=f"FAQ Answer {i}")
#         if q.strip() and a.strip():
#             faq_data.append({"question": q, "answer": a})

# # --- PROCESS & GENERATE HTML ---
# st.markdown("---")
# if st.button("🚀 Generate & Save Article", type="primary", use_container_width=True):
#     if not title or not content or not slug:
#         st.error("❌ Please provide a Title, Slug, and Main Body Content to build the article.")
#     else:
#         # 1. Process Takeaways
#         takeaways_list = [line.strip() for line in takeaways_input.split("\n") if line.strip()]
#         takeaways_html = "".join(f"<li>{item}</li>" for item in takeaways_list)
#         if takeaways_html:
#             takeaways_html = f"<div class='takeaways'><h3>Key Takeaways</h3><ul>{takeaways_html}</ul></div>"

#         # 2. Process Image Alignment
#         image_html = ""
#         if uploaded_file is not None:
#             # Save the image into site/images/
#             img_path = os.path.join(IMAGES_DIR, uploaded_file.name)
#             with open(img_path, "wb") as f:
#                 f.write(uploaded_file.getbuffer())
            
#             # The generated HTML is inside site/knowledge/, so it jumps up one folder to reach site/images/
#             relative_img_src = f"../images/{uploaded_file.name}"
            
#             if "Left" in alignment:
#                 image_html = f'<img src="{relative_img_src}" style="float: left; margin: 0 20px 20px 0; max-width: 40%; height: auto; border-radius: 8px;">'
#             elif "Right" in alignment:
#                 image_html = f'<img src="{relative_img_src}" style="float: right; margin: 0 0 20px 20px; max-width: 40%; height: auto; border-radius: 8px;">'
#             else:
#                 image_html = f'<div style="text-align: center; margin-bottom: 20px;"><img src="{relative_img_src}" style="max-width: 80%; height: auto; border-radius: 8px;"></div>'

#         # 3. Process FAQs
#         faq_html = ""
#         if faq_data:
#             faq_items = "".join(f"<div class='faq-item'><h4>{f['question']}</h4><p>{f['answer']}</p></div>" for f in faq_data)
#             faq_html = f"<div class='faq-section'><h3>Frequently Asked Questions</h3>{faq_items}</div>"

#         # 4. Standardized HTML Template matching your site structure
#         html_template = f"""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>{title}</title>
#     <meta name="description" content="{meta_desc}">
#     <style>
#         body {{
#             font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
#             line-height: 1.6;
#             color: #333;
#             max-width: 850px;
#             margin: 40px auto;
#             padding: 0 20px;
#         }}
#         .meta-bar {{
#             font-size: 0.9rem;
#             color: #666;
#             margin-bottom: 20px;
#             border-bottom: 1px solid #eee;
#             padding-bottom: 10px;
#         }}
#         .category {{
#             background: #eef2f6;
#             color: #1d4ed8;
#             padding: 3px 8px;
#             border-radius: 4px;
#             font-weight: 600;
#         }}
#         h1 {{ font-size: 2.6rem; color: #111; margin-bottom: 10px; line-height: 1.2; }}
#         .takeaways {{
#             background-color: #f8fafc;
#             border-left: 4px solid #0f172a;
#             padding: 15px 20px;
#             margin: 25px 0;
#             border-radius: 0 8px 8px 0;
#         }}
#         .takeaways h3 {{ margin-top: 0; color: #0f172a; }}
#         .prose {{ font-size: 1.15rem; color: #222; }}
#         .faq-section {{ margin-top: 40px; border-top: 2px solid #e2e8f0; padding-top: 20px; }}
#         .faq-item {{ margin-bottom: 20px; }}
#         .faq-item h4 {{ font-size: 1.2rem; color: #0f172a; margin-bottom: 5px; }}
#         .clearfix::after {{ content: ""; clear: both; display: table; }}
#     </style>
# </head>
# <body>

#     <span class="category">{category}</span>
#     <h1>{title}</h1>
#     <div class="meta-bar">
#         <span>Published on: {publish_date.strftime('%B %d, %Y')}</span> | <span>⏱ {read_time} read</span>
#     </div>
    
#     {takeaways_html}
    
#     <div class="prose clearfix">
#         {image_html}
#         {content.replace('\\n', '<br><br>')}
#     </div>
    
#     {faq_html}

# </body>
# </html>
# """

#         # Ensure correct extension and build file destination path
#         final_filename = slug.strip() if slug.endswith(".html") else f"{slug.strip()}.html"
#         file_path = os.path.join(KNOWLEDGE_DIR, final_filename)
        
#         # Write template down to the disk
#         with open(file_path, "w", encoding="utf-8") as f:
#             f.write(html_template)
            
#         st.success(f"✅ Article successfully created at: `{file_path}`")
#         st.balloons()




















# import streamlit as st
# import os
# import datetime

# # --- CONFIGURATION & PATHS ---
# SITE_DIR = "site"
# KNOWLEDGE_DIR = os.path.join(SITE_DIR, "knowledge")
# IMAGES_DIR = os.path.join(SITE_DIR, "images")
# # Updated to point exactly to your CSS file path 🎯
# CSS_FILE_PATH = os.path.join(SITE_DIR, "assets", "site.css") 

# # Ensure directories exist
# os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
# os.makedirs(IMAGES_DIR, exist_ok=True)

# # Page Setup
# st.set_page_config(page_title="Arcubus Publisher Pro", page_icon="📝", layout="wide")

# st.title("🚀 Arcubus Knowledge Center Publisher")
# st.write("Fill out the structural forms below to match your terminal script workflow.")

# # --- SIDE-BY-SIDE INTERFACE BLOCKS ---
# col1, col2 = st.columns(2, gap="large")

# with col1:
#     st.subheader("📋 1. Article Information & Metadata")
#     title = st.text_input("1. Article Title (Headline)", placeholder="How to choose the right transfer pricing method...")
    
#     default_slug = "".join(c for c in title.lower() if c.isalnum() or c in " ").replace(" ", "-")
#     slug = st.text_input("2. Filename / Slug (without .html)", placeholder="choosing-transfer-pricing-method-intra-group-services", value=default_slug)
    
#     category = st.text_input("3. Category", placeholder="Transfer Pricing Methods, Benchmarking, etc.")
#     publish_date = st.date_input("4. Publish Date", value=datetime.date.today())
#     meta_desc = st.text_area("5. Meta Description (150-160 chars)", max_chars=160, placeholder="A practical guide...")
#     read_time = st.text_input("6. Estimated Read Time", placeholder="e.g., 6 min")

#     st.subheader("💡 2. Key Takeaways")
#     takeaways_input = st.text_area("7. Enter 3–5 points (one per line):", height=130, placeholder="Point 1\nPoint 2\nPoint 3")

#     st.subheader("❓ 5. Frequently Asked Questions (Optional)")
#     faq_data = []
#     for i in range(1, 3):
#         q = st.text_input(f"Question {i}:", key=f"q_{i}")
#         a = st.text_area(f"Answer {i}:", key=f"a_{i}", height=70)
#         if q.strip() and a.strip():
#             faq_data.append({"question": q, "answer": a})

# with col2:
#     st.subheader("🖼️ 3. Article Images (Upload up to 2 Images)")
    
#     images_html_list = []
    
#     # Image 1 block
#     st.markdown("**Image Module 1**")
#     file1 = st.file_uploader("Choose First Image", type=["png", "jpg", "jpeg", "webp"], key="img_1")
#     align1 = st.radio("Alignment for Image 1", ["Left Wrap", "Center Break", "Right Wrap"], key="align_1", horizontal=True)
    
#     if file1 is not None:
#         img_path1 = os.path.join(IMAGES_DIR, file1.name)
#         with open(img_path1, "wb") as f:
#             f.write(file1.getbuffer())
        
#         # Relative path from site/knowledge/ to site/images/
#         rel_path1 = f"../images/{file1.name}"
#         if "Left" in align1:
#             images_html_list.append(f'<img src="{rel_path1}" style="float: left; margin: 0 20px 20px 0; max-width: 45%; height: auto; border-radius: 6px;">')
#         elif "Right" in align1:
#             images_html_list.append(f'<img src="{rel_path1}" style="float: right; margin: 0 0 20px 20px; max-width: 45%; height: auto; border-radius: 6px;">')
#         else:
#             images_html_list.append(f'<div style="text-align: center; margin: 20px 0;"><img src="{rel_path1}" style="max-width: 80%; height: auto; border-radius: 6px;"></div>')

#     st.markdown("---")
    
#     # Image 2 block (Simulating your second loop condition)
#     st.markdown("**Image Module 2**")
#     file2 = st.file_uploader("Choose Second Image (Optional)", type=["png", "jpg", "jpeg", "webp"], key="img_2")
#     align2 = st.radio("Alignment for Image 2", ["Left Wrap", "Center Break", "Right Wrap"], key="align_2", horizontal=True)
    
#     if file2 is not None:
#         img_path2 = os.path.join(IMAGES_DIR, file2.name)
#         with open(img_path2, "wb") as f:
#             f.write(file2.getbuffer())
        
#         # Relative path from site/knowledge/ to site/images/
#         rel_path2 = f"../images/{file2.name}"
#         if "Left" in align2:
#             images_html_list.append(f'<img src="{rel_path2}" style="float: left; margin: 0 20px 20px 0; max-width: 45%; height: auto; border-radius: 6px;">')
#         elif "Right" in align2:
#             images_html_list.append(f'<img src="{rel_path2}" style="float: right; margin: 0 0 20px 20px; max-width: 45%; height: auto; border-radius: 6px;">')
#         else:
#             images_html_list.append(f'<div style="text-align: center; margin: 20px 0;"><img src="{rel_path2}" style="max-width: 80%; height: auto; border-radius: 6px;"></div>')

#     st.subheader("🖋️ 4. Article Main Body Content")
#     content = st.text_area("8. Paste text formatting inside <div class='prose'>:", height=200, placeholder="Type layout here...")

# # --- GENERATE & EXPORT ENGINE ---
# st.markdown("---")
# if st.button("🚀 Generate & Save Article", type="primary", use_container_width=True):
#     if not title or not content or not slug:
#         st.error("❌ Required fields missing (Title, Slug, or Content Body).")
#     else:
#         # Load your live system CSS content safely from site/assets/site.css
#         custom_css_content = ""
#         if os.path.exists(CSS_FILE_PATH):
#             with open(CSS_FILE_PATH, "r", encoding="utf-8") as css_file:
#                 custom_css_content = f"<style>{css_file.read()}</style>"
#         else:
#             # Fallback styling if file path isn't found
#             st.warning(f"⚠️ Could not find CSS file at `{CSS_FILE_PATH}`. Using basic fallback styles.")
#             custom_css_content = """<style>
#                 body { font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 20px; }
#                 .clearfix::after { content: ""; clear: both; display: table; }
#             </style>"""

#         # Build Takeaways structural arrays
#         takeaways_list = [line.strip() for line in takeaways_input.split("\n") if line.strip()]
#         takeaways_html = "".join(f"<li>{item}</li>" for item in takeaways_list)
#         if takeaways_html:
#             takeaways_html = f"<div class='takeaways'><h3>Key Takeaways</h3><ul>{takeaways_html}</ul></div>"

#         # Build combined content body strings layout
#         images_injected_html = "".join(images_html_list)
        
#         # Build FAQ sections
#         faq_html = ""
#         if faq_data:
#             faq_items = "".join(f"<div class='faq-item'><h4>{f['question']}</h4><p>{f['answer']}</p></div>" for f in faq_data)
#             faq_html = f"<div class='faq-section'><h3>Frequently Asked Questions</h3>{faq_items}</div>"

#         # Construct final unified production HTML file matching your project specs
#         html_template = f"""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>{title}</title>
#     <meta name="description" content="{meta_desc}">
#     {custom_css_content}
# </head>
# <body>

#     <span class="category">{category}</span>
#     <h1>{title}</h1>
#     <div class="meta-bar">
#         <span>Published: {publish_date.strftime('%B %d, %Y')}</span> | <span>⏱ {read_time}</span>
#     </div>
    
#     {takeaways_html}
    
#     <div class="prose clearfix">
#         {images_injected_html}
#         {content.replace('\\n', '<br><br>')}
#     </div>
    
#     {faq_html}

# </body>
# </html>
# """

#         # Output to directory file
#         final_filename = slug.strip() if slug.endswith(".html") else f"{slug.strip()}.html"
#         file_path = os.path.join(KNOWLEDGE_DIR, final_filename)
        
#         with open(file_path, "w", encoding="utf-8") as f:
#             f.write(html_template)
            
#         st.success(f"🎉 File updated! Saved to: `{file_path}`")












import streamlit as st
import os
import datetime

# --- CONFIGURATION & PATHS ---
SITE_DIR = "site"
KNOWLEDGE_DIR = os.path.join(SITE_DIR, "knowledge")
IMAGES_DIR = os.path.join(SITE_DIR, "images")
CSS_FILE_PATH = os.path.join(SITE_DIR, "assets", "site.css") 

# Ensure directories exist
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Page Setup
st.set_page_config(page_title="Arcubus Dynamic Publisher", page_icon="📝", layout="wide")

st.title("🚀 Arcubus Dynamic Knowledge Publisher")
st.write("Construct complex article layouts with up to 10 images mixed completely throughout your paragraphs.")

# Use modern columns layout split
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📋 1. Article Information & Metadata")
    title = st.text_input("Article Title (Headline)", placeholder="How to choose the right transfer pricing method...")
    
    default_slug = "".join(c for c in title.lower() if c.isalnum() or c in " ").replace(" ", "-")
    slug = st.text_input("Filename / Slug (without .html)", placeholder="choosing-transfer-pricing-method-intra-group-services", value=default_slug)
    
    category = st.text_input("Category", placeholder="Transfer Pricing Methods")
    publish_date = st.date_input("Publish Date", value=datetime.date.today())
    meta_desc = st.text_area("Meta Description (150-160 chars)", max_chars=160)
    read_time = st.text_input("Estimated Read Time", placeholder="e.g., 6 min")

    st.subheader("💡 2. Key Takeaways")
    takeaways_input = st.text_area("Enter 3–5 points (one per line):", height=100)

    st.subheader("❓ 4. Frequently Asked Questions (Optional)")
    faq_data = []
    for i in range(1, 3):
        q = st.text_input(f"Question {i}:", key=f"q_{i}")
        a = st.text_area(f"Answer {i}:", key=f"a_{i}", height=60)
        if q.strip() and a.strip():
            faq_data.append({"question": q, "answer": a})

with col2:
    st.subheader("🖼️ 3. Dynamic Image Repository (Up to 10 Images)")
    st.info("💡 Upload images below, then drop `[IMAGE1]`, `[IMAGE2]`, etc. inside your main body text exactly where you want them to appear!")
    
    # Store dynamic image arrays inside a structure dictionary
    images_registry = {}
    
    # Create an expander loop mapping out up to 10 images cleanly
    with st.expander("Expand to upload and align images", expanded=True):
        for idx in range(1, 11):
            file_key = f"img_{idx}"
            align_key = f"align_{idx}"
            
            uploaded_file = st.file_uploader(f"Image Slot {idx}", type=["png", "jpg", "jpeg", "webp"], key=file_key)
            alignment = st.radio(f"Alignment for Slot {idx}", ["Left Wrap", "Center Break", "Right Wrap"], key=align_key, horizontal=True)
            
            if uploaded_file is not None:
                # Instantly drop item contents onto server system directory
                img_path = os.path.join(IMAGES_DIR, uploaded_file.name)
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Assign formatting properties back to registry mappings
                rel_src = f"../images/{uploaded_file.name}"
                if "Left" in alignment:
                    img_tag = f'<img src="{rel_src}" style="float: left; margin: 0 20px 20px 0; max-width: 45%; height: auto; border-radius: 6px;">'
                elif "Right" in alignment:
                    img_tag = f'<img src="{rel_src}" style="float: right; margin: 0 0 20px 20px; max-width: 45%; height: auto; border-radius: 6px;">'
                else:
                    img_tag = f'<div style="text-align: center; margin: 25px 0;"><img src="{rel_src}" style="max-width: 80%; height: auto; border-radius: 6px;"></div>'
                
                images_registry[f"[IMAGE{idx}]"] = img_tag
            
            if idx < 10:
                st.markdown("---")

    st.subheader("🖋️ 4. Article Main Body Content")
    st.caption("Wrap text chunks with standard HTML formatting tags or basic block formatting if needed.")
    content = st.text_area("Main Body Input Area:", height=250, 
                           placeholder="Choosing the correct method is critical.\n\n[IMAGE1]\n\nThis text paragraph right here will display beside image 1 if image 1 is set to Left or Right Wrap! If the paragraph text is long enough, it will flow beautifully underneath it.\n\n[IMAGE2]\n\nThis text will appear down below near the second image block.")

# --- COMPILATION ENGINE ---
st.markdown("---")
if st.button("🚀 Generate & Save Dynamic Article", type="primary", use_container_width=True):
    if not title or not content or not slug:
        st.error("❌ Required fields missing (Title, Slug, or Content Body).")
    else:
        # Load production stylesheet
        custom_css_content = ""
        if os.path.exists(CSS_FILE_PATH):
            with open(CSS_FILE_PATH, "r", encoding="utf-8") as css_file:
                custom_css_content = f"<style>{css_file.read()}</style>"
        else:
            st.warning(f"⚠️ Could not find CSS file at `{CSS_FILE_PATH}`. Using basic fallback styles.")
            custom_css_content = """<style>
                body { font-family: sans-serif; line-height: 1.6; max-width: 850px; margin: 40px auto; padding: 20px; text-align: justify; }
                .clearfix::after { content: ""; clear: both; display: table; }
                .prose p { text-align: justify; }
            </style>"""

        # Build Takeaways
        takeaways_list = [line.strip() for line in takeaways_input.split("\n") if line.strip()]
        takeaways_html = "".join(f"<li>{item}</li>" for item in takeaways_list)
        if takeaways_html:
            takeaways_html = f"<div class='takeaways'><h3>Key Takeaways</h3><ul>{takeaways_html}</ul></div>"

        # Transform paragraphs and break strings
        processed_content = content.replace('\n', '<br>')
        
        # Parse content layout strings and swap codes with dynamic structural image styles
        for token, image_html in images_registry.items():
            processed_content = processed_content.replace(token, image_html)

        # Build FAQs
        faq_html = ""
        if faq_data:
            faq_items = "".join(f"<div class='faq-item'><h4>{f['question']}</h4><p>{f['answer']}</p></div>" for f in faq_data)
            faq_html = f"<div class='faq-section'><h3>Frequently Asked Questions</h3>{faq_items}</div>"

        # Global assembly template matching site rules layout
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    {custom_css_content}
</head>
<body>

    <span class="category">{category}</span>
    <h1>{title}</h1>
    <div class="meta-bar">
        <span>Published: {publish_date.strftime('%B %d, %Y')}</span> | <span>⏱ {read_time}</span>
    </div>
    
    {takeaways_html}
    
    <div class="prose clearfix" style="text-align: justify;">
        {processed_content}
    </div>
    
    {faq_html}

</body>
</html>
"""

        # Save to knowledge directory
        final_filename = slug.strip() if slug.endswith(".html") else f"{slug.strip()}.html"
        file_path = os.path.join(KNOWLEDGE_DIR, final_filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_template)
            
        st.success(f"🎉 Dynamic article successfully generated at: `{file_path}`")
