#!/usr/bin/env python3
"""Convert Prabhupada letter .txt files into vedabase-app HTML files (let1-4.html)."""

import os
import re
import html

LETTERS_DIR = os.path.expanduser("~/.emacs.d/git_projects/vedabase/letters")
OUTPUT_DIR = os.path.expanduser(
    "~/.emacs.d/git_projects/bhagavad-gita-app/vedabase-app/vedabase-source"
)

# Split into 4 parts by year range
SPLITS = [
    ("let1.html", "Letters 1947-1968", 1947, 1968),
    ("let2.html", "Letters 1969-1971", 1969, 1971),
    ("let3.html", "Letters 1972-1974", 1972, 1974),
    ("let4.html", "Letters 1975-1977", 1975, 1977),
]

HEAD_TEMPLATE = """\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<meta name="author" content="A.C. Bhaktivedanta Swami Prabhupada" />
<link rel="stylesheet" type="text/css" href="css/htmlize.css"/>
<link rel="stylesheet" type="text/css" href="css/readtheorg.css"/>
<script src="js/jquery.min.js"></script>
<script src="js/bootstrap.min.js"></script>
<script type="text/javascript" src="js/jquery.stickytableheaders.min.js"></script>
<script type="text/javascript" src="js/readtheorg.js"></script>
<script src="collapse-script.js"></script>
<style id="toc-force-collapse">
#text-table-of-contents ul ul {{ display: none !important; }}
#text-table-of-contents li.expanded > ul {{ display: block !important; }}
#text-table-of-contents li:before {{ display: none !important; }}
.toc-indicator {{ display: none !important; }}
</style>
<style id="dark-mode-styles">
body.dark-mode, body.dark-mode *, body.dark-mode html, body.dark-mode div,
body.dark-mode span, body.dark-mode p, body.dark-mode h1, body.dark-mode h2,
body.dark-mode h3, body.dark-mode h4, body.dark-mode h5, body.dark-mode h6,
body.dark-mode li, body.dark-mode td, body.dark-mode th, body.dark-mode table,
body.dark-mode thead, body.dark-mode tbody, body.dark-mode tr,
body.dark-mode blockquote, body.dark-mode pre, body.dark-mode code,
body.dark-mode .content, body.dark-mode #content,
body.dark-mode #text-table-of-contents {{
    background-color: #000000 !important;
    background: #000000 !important;
}}
body.dark-mode, body.dark-mode *, body.dark-mode p, body.dark-mode h1,
body.dark-mode h2, body.dark-mode h3, body.dark-mode h4, body.dark-mode h5,
body.dark-mode h6, body.dark-mode div, body.dark-mode span, body.dark-mode li,
body.dark-mode td, body.dark-mode th, body.dark-mode blockquote,
body.dark-mode pre, body.dark-mode code, body.dark-mode dt, body.dark-mode dd,
body.dark-mode .content, body.dark-mode #content,
body.dark-mode #text-table-of-contents {{
    color: #ffffff !important;
}}
body.dark-mode a, body.dark-mode a *, body.dark-mode a:visited,
body.dark-mode a:hover {{
    color: #60a5fa !important;
}}
</style>
</head>
<body>
<div id="content" class="content">
<h1 class="title">{title}
<br />
<span class="subtitle">by A. C. Bhaktivedanta Swami Prabhupada</span>
</h1>
<div id="table-of-contents" role="doc-toc">
<h2>Table of Contents</h2>
<div id="text-table-of-contents" role="doc-toc">
<ul>
"""

FOOT_TEMPLATE = """\
</div>
<div id="postamble" class="status">
<p class="author">Author: A.C. Bhaktivedanta Swami Prabhupada</p>
</div>
<script src="font-control.js"></script></body>
</html>
"""


def parse_letter(filepath):
    """Parse a letter .txt file and return metadata + body."""
    with open(filepath, "r", errors="replace") as f:
        content = f.read()

    # Extract title from ~~Title: ...~~
    title_match = re.search(r"~~Title:\s*(.+?)~~", content)
    title = title_match.group(1).strip() if title_match else os.path.basename(filepath)

    # Extract metadata
    recipient = ""
    date = ""
    year = 0
    place = ""

    r_match = re.search(r"To_letters\s*:\s*(.+)", content)
    if r_match:
        recipient = r_match.group(1).strip()

    d_match = re.search(r"Date_letter\s*:\s*(.+)", content)
    if d_match:
        date = d_match.group(1).strip()

    y_match = re.search(r"Year_letter\s*:\s*(\d+)", content)
    if y_match:
        year = int(y_match.group(1))

    p_match = re.search(r"Place_letter\s*:\s*(.+)", content)
    if p_match:
        place = p_match.group(1).strip()

    # Extract body: everything after the ---- (second separator)
    parts = content.split("----")
    if len(parts) >= 3:
        body = parts[-1].strip()
    else:
        # Fallback: skip header lines
        lines = content.split("\n")
        body_start = 0
        for i, line in enumerate(lines):
            if line.startswith("----") and i > 5:
                body_start = i + 1
                break
        body = "\n".join(lines[body_start:]).strip()

    # Extract year from filename if not in metadata
    if year == 0:
        fname = os.path.basename(filepath)
        m = re.match(r"(\d{2})", fname)
        if m:
            yy = int(m.group(1))
            year = 1900 + yy if yy > 30 else 2000 + yy

    return {
        "title": title,
        "recipient": recipient,
        "date": date,
        "year": year,
        "place": place,
        "body": body,
        "filename": os.path.basename(filepath),
    }


def body_to_html(body):
    """Convert letter body text to HTML paragraphs."""
    # Escape ampersands first (before any HTML tags are inserted)
    body = body.replace("&", "&amp;")

    # Handle the wiki-style line breaks \\
    body = body.replace("\\\\", "<br />")

    # Handle __underline__ -> <u>
    body = re.sub(r"__(.+?)__", r"<u>\1</u>", body)

    # Handle **bold** -> <b>
    body = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", body)

    # Split into paragraphs on blank lines
    paragraphs = re.split(r"\n\s*\n", body)

    html_parts = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Preserve line breaks within paragraph
        para = para.replace("\n", "<br />\n")
        html_parts.append(f"<p>\n{para}\n</p>")

    return "\n".join(html_parts)


def make_toc_title(letter):
    """Create a short TOC entry."""
    if letter["recipient"] and letter["date"]:
        return f"{letter['recipient']} — {letter['date']}, {letter['year']}"
    return letter["title"]


def build_html(filename, title, letters):
    """Build a single HTML file from a list of letters."""
    # Build TOC - group by year
    toc_items = []
    current_year = None
    for i, letter in enumerate(letters):
        anchor = f"let{i:05d}"
        toc_title = html.escape(make_toc_title(letter))

        if letter["year"] != current_year:
            if current_year is not None:
                toc_items.append("</ul>\n</li>")
            current_year = letter["year"]
            year_anchor = f"year{current_year}"
            toc_items.append(
                f'<li><a href="#{year_anchor}">{current_year}</a>\n<ul>'
            )

        toc_items.append(f'<li><a href="#{anchor}">{toc_title}</a></li>')

    if current_year is not None:
        toc_items.append("</ul>\n</li>")

    # Build content sections
    sections = []
    current_year = None
    for i, letter in enumerate(letters):
        anchor = f"let{i:05d}"

        # Year heading
        if letter["year"] != current_year:
            if current_year is not None:
                sections.append("</div>\n</div>")  # close previous year
            current_year = letter["year"]
            year_anchor = f"year{current_year}"
            sections.append(
                f'<div id="outline-container-{year_anchor}" class="outline-2">\n'
                f'<h2 id="{year_anchor}">{current_year}</h2>\n'
                f'<div class="outline-text-2">'
            )

        # Letter section
        letter_title = html.escape(make_toc_title(letter))
        body_html = body_to_html(letter["body"])

        # Add place info if available
        place_line = ""
        if letter["place"]:
            place_line = f'<p><i>{html.escape(letter["place"])}</i></p>\n'

        sections.append(
            f'<div id="outline-container-{anchor}" class="outline-3">\n'
            f'<h3 id="{anchor}">{letter_title}</h3>\n'
            f'<div class="outline-text-3">\n'
            f'{place_line}'
            f'{body_html}\n'
            f'</div>\n</div>'
        )

    if current_year is not None:
        sections.append("</div>\n</div>")  # close last year

    out = HEAD_TEMPLATE.format(title=title)
    out += "\n".join(toc_items)
    out += "\n</ul>\n</div>\n</div>\n"
    out += "\n".join(sections)
    out += FOOT_TEMPLATE

    outpath = os.path.join(OUTPUT_DIR, filename)
    with open(outpath, "w") as f:
        f.write(out)
    size_mb = os.path.getsize(outpath) / (1024 * 1024)
    print(f"  {filename}: {len(letters)} letters, {size_mb:.1f} MB")


def main():
    print("Loading letters...")
    letters = []
    skipped = 0
    for fname in sorted(os.listdir(LETTERS_DIR)):
        if not fname.endswith(".txt"):
            continue
        if fname.startswith("_"):
            # Skip template/special files
            skipped += 1
            continue
        path = os.path.join(LETTERS_DIR, fname)
        letter = parse_letter(path)
        if letter["body"]:
            letters.append(letter)

    # Sort by year, then by filename (which has date prefix)
    letters.sort(key=lambda l: (l["year"], l["filename"]))
    print(f"  Loaded {len(letters)} letters (skipped {skipped} special files)")

    for filename, title, year_start, year_end in SPLITS:
        subset = [l for l in letters if year_start <= l["year"] <= year_end]
        print(f"\nBuilding {filename} ({year_start}-{year_end})...")
        build_html(filename, title, subset)

    # Check for letters with no year
    no_year = [l for l in letters if l["year"] == 0]
    if no_year:
        print(f"\nWarning: {len(no_year)} letters with no year:")
        for l in no_year[:5]:
            print(f"  {l['filename']}: {l['title'][:60]}")

    print("\nDone!")


if __name__ == "__main__":
    main()
