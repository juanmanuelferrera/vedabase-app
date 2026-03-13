#!/usr/bin/env python3
"""Generate letters HTML files for the vedabase app from letter text files."""

import os
import re
import html

LETTERS_DIR = "/Users/jaganat/.emacs.d/git_projects/vedabase/letters/"
OUTPUT_DIR = "/Users/jaganat/.emacs.d/git_projects/vedabase-app-website/vedabase-app/vedabase-source/"

# Split into 4 parts by year ranges for manageable file sizes
SPLITS = [
    ("let1.html", "Letters 1947–1969", lambda y: y <= 1969),
    ("let2.html", "Letters 1970–1972", lambda y: 1970 <= y <= 1972),
    ("let3.html", "Letters 1973–1974", lambda y: 1973 <= y <= 1974),
    ("let4.html", "Letters 1975–1977", lambda y: 1975 <= y <= 1977),
]

DARK_MODE_CSS = """<style id="dark-mode-styles">
body.dark-mode, body.dark-mode *, body.dark-mode html, body.dark-mode div,
body.dark-mode span, body.dark-mode p, body.dark-mode h1, body.dark-mode h2,
body.dark-mode h3, body.dark-mode h4, body.dark-mode h5, body.dark-mode h6,
body.dark-mode li, body.dark-mode td, body.dark-mode th, body.dark-mode table,
body.dark-mode thead, body.dark-mode tbody, body.dark-mode tr,
body.dark-mode blockquote, body.dark-mode pre, body.dark-mode code,
body.dark-mode .content, body.dark-mode #content,
body.dark-mode #text-table-of-contents {
    background-color: #000000 !important;
    background: #000000 !important;
}
body.dark-mode, body.dark-mode p, body.dark-mode span, body.dark-mode div,
body.dark-mode li, body.dark-mode td, body.dark-mode th, body.dark-mode h1,
body.dark-mode h2, body.dark-mode h3, body.dark-mode h4, body.dark-mode h5,
body.dark-mode h6, body.dark-mode blockquote, body.dark-mode a,
body.dark-mode #text-table-of-contents a {
    color: #e0e0e0 !important;
}
body.dark-mode a:hover, body.dark-mode #text-table-of-contents a:hover {
    color: #ffffff !important;
}
body.dark-mode hr { border-color: #333 !important; }
body.dark-mode .letter-meta { color: #aaa !important; }
</style>"""


def parse_letter(filepath):
    """Parse a letter text file and return structured data."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Extract title from ~~Title: ...~~
    title_match = re.search(r"~~Title:\s*(.+?)~~", text)
    title = title_match.group(1).strip() if title_match else os.path.basename(filepath)

    # Extract metadata
    recipient = ""
    date_str = ""
    year = 0
    place = ""

    for line in text.split("\n"):
        if line.startswith("To_letters"):
            recipient = line.split(":", 1)[1].strip()
        elif line.startswith("Date_letter"):
            date_str = line.split(":", 1)[1].strip()
        elif line.startswith("Year_letter"):
            try:
                year = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("Place_letter"):
            place = line.split(":", 1)[1].strip()

    # Extract body: everything after the ---- (second one) metadata block
    body = ""
    lines = text.split("\n")
    dash_count = 0
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "----":
            dash_count += 1
            if dash_count == 2:
                body_start = i + 1
                break

    if body_start:
        body = "\n".join(lines[body_start:]).strip()
    else:
        # Fallback: skip headers, take from "My dear" or first paragraph
        for i, line in enumerate(lines):
            if line.startswith("My dear") or line.startswith("My Dear"):
                body = "\n".join(lines[i:]).strip()
                break

    return {
        "title": title,
        "recipient": recipient,
        "date": date_str,
        "year": year,
        "place": place,
        "body": body,
        "filename": os.path.basename(filepath),
    }


def letter_to_html(letter):
    """Convert a parsed letter to HTML fragment."""
    safe_id = re.sub(r"[^a-zA-Z0-9]", "_", letter["filename"].replace(".txt", ""))

    meta_parts = []
    if letter["date"] and letter["year"]:
        meta_parts.append(f"{letter['date']}, {letter['year']}")
    elif letter["year"]:
        meta_parts.append(str(letter["year"]))
    if letter["place"]:
        meta_parts.append(letter["place"])

    meta_line = " — ".join(meta_parts) if meta_parts else ""

    # Convert body text to HTML paragraphs
    body_html = ""
    for para in letter["body"].split("\n\n"):
        para = para.strip()
        if not para:
            continue
        # Handle line breaks within paragraphs (backslash-newline)
        para = para.replace("\\\n", "<br/>\n")
        para = html.escape(para).replace("&lt;br/&gt;", "<br/>")
        body_html += f"<p>{para}</p>\n"

    return f'''<div id="outline-container-{safe_id}" class="outline-3">
<h3 id="{safe_id}">{html.escape(letter["title"])}</h3>
<div class="outline-text-3">
<p class="letter-meta"><em>{html.escape(meta_line)}</em></p>
{body_html}
</div>
</div>
'''


def generate_html(filename, part_title, letters):
    """Generate a full HTML page for a set of letters."""
    # Build TOC
    toc_items = []
    for lt in letters:
        safe_id = re.sub(r"[^a-zA-Z0-9]", "_", lt["filename"].replace(".txt", ""))
        display = lt["title"]
        toc_items.append(f'<li><a href="#{safe_id}">{html.escape(display)}</a></li>')

    toc_html = "\n".join(toc_items)

    # Build content
    content_html = ""
    for lt in letters:
        content_html += letter_to_html(lt)

    page = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(part_title)}</title>
<meta name="author" content="A.C. Bhaktivedanta Swami Prabhupada" />
<link rel="stylesheet" type="text/css" href="https://fniessen.github.io/org-html-themes/src/readtheorg_theme/css/htmlize.css"/>
<link rel="stylesheet" type="text/css" href="https://fniessen.github.io/org-html-themes/src/readtheorg_theme/css/readtheorg.css"/>
<link rel="stylesheet" type="text/css" href="src/readtheorg_theme/css/search.css"/>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
<script type="text/javascript" src="https://fniessen.github.io/org-html-themes/src/lib/js/jquery.stickytableheaders.min.js"></script>
<script type="text/javascript" src="https://fniessen.github.io/org-html-themes/src/readtheorg_theme/js/search.js"></script>
<script type="text/javascript" src="https://fniessen.github.io/org-html-themes/src/readtheorg_theme/js/readtheorg.js"></script>
{DARK_MODE_CSS}
</head>
<body>
<div id="content" class="content">
<h1 class="title">{html.escape(part_title)}</h1>
<div id="table-of-contents" role="doc-toc">
<h2>Table of Contents</h2>
<div id="text-table-of-contents" role="doc-toc">
<ul>
<li><a href="#letters-main">{html.escape(part_title)}</a>
<ul>
{toc_html}
</ul>
</li>
</ul>
</div>
</div>

<div id="outline-container-letters-main" class="outline-2">
<h2 id="letters-main">{html.escape(part_title)}</h2>
<div class="outline-text-2" id="text-letters-main">
<p>
His Divine Grace
</p>
<p>
A.C. Bhaktivedanta Swami Prabhupada
</p>
<p>
Founder-Acarya of the International Society for Krishna Consciousness
</p>
</div>

{content_html}
</div>
</div>
<div id="postamble" class="status">
</div>
</body>
</html>'''

    outpath = os.path.join(OUTPUT_DIR, filename)
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(page)

    size_mb = os.path.getsize(outpath) / (1024 * 1024)
    print(f"  {filename}: {len(letters)} letters, {size_mb:.1f} MB")


def main():
    print("Generating letters HTML files...\n")

    # Parse all letters
    all_letters = []
    special = []  # Files starting with _
    for fname in sorted(os.listdir(LETTERS_DIR)):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(LETTERS_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        lt = parse_letter(fpath)
        if fname.startswith("_"):
            special.append(lt)
        else:
            all_letters.append(lt)

    # Sort by filename (which is date-based: YYMMDD_recipient.txt)
    all_letters.sort(key=lambda x: x["filename"])

    print(f"Parsed {len(all_letters)} dated letters + {len(special)} special files\n")

    # Generate each split
    for filename, title, year_filter in SPLITS:
        letters = [lt for lt in all_letters if year_filter(lt["year"])]
        # Add special files to the first split
        if filename == "let1.html":
            letters = special + letters
        generate_html(filename, title, letters)

    print("\nDone!")


if __name__ == "__main__":
    main()
