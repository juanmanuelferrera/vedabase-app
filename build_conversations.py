#!/usr/bin/env python3
"""Convert Conversations epub sections into vedabase-app HTML files (conv1-3.html)."""

import os
import re
from html.parser import HTMLParser

EPUB_DIR = os.path.expanduser(
    "~/.emacs.d/git_projects/questions_answers/Conversations.epub"
)
OUTPUT_DIR = os.path.expanduser(
    "~/.emacs.d/git_projects/bhagavad-gita-app/vedabase-app/vedabase-source"
)

# Split into 3 parts (matching lecture split pattern of ~350 per file)
SPLITS = [
    ("conv1.html", "Conversations Part 1 (1967-1973)", 1967, 1973),
    ("conv2.html", "Conversations Part 2 (1974-1975)", 1974, 1975),
    ("conv3.html", "Conversations Part 3 (1976-1977)", 1976, 1977),
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


class BodyExtractor(HTMLParser):
    """Extract text content from epub body, converting to simple paragraphs."""

    def __init__(self):
        super().__init__()
        self.in_body = False
        self.paragraphs = []
        self.current = []
        self.current_tag = None
        self.bold = False

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        cls = attrs_d.get("class", "")
        if tag == "body":
            self.in_body = True
            return
        if not self.in_body:
            return
        if tag == "div" and cls in ("Verse-Number", "Conv-code", "Heading"):
            # Skip these header divs - we use our own heading
            self.current_tag = cls
            self.current = []
        elif tag == "div" and cls in ("Purp-para", "Syn-title-no-indent",
                                       "Syn-title", "Text-pr", "Text-pr-no-indent",
                                       ""):
            self.current_tag = "para"
            self.current = []
        elif tag == "span" and cls == "Bold":
            self.bold = True
        elif tag == "br":
            pass

    def handle_endtag(self, tag):
        if tag == "body":
            self.in_body = False
            return
        if not self.in_body:
            return
        if tag == "span" and self.bold:
            self.bold = False
        elif tag == "div" and self.current_tag:
            text = "".join(self.current).strip()
            if text and self.current_tag == "para":
                self.paragraphs.append(text)
            self.current_tag = None
            self.current = []

    def handle_data(self, data):
        if not self.in_body or not self.current_tag:
            return
        if self.current_tag in ("Verse-Number", "Conv-code"):
            return  # skip
        # Escape for XHTML
        data = data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if self.bold:
            self.current.append(f"<b>{data}</b>")
        else:
            self.current.append(data)


def extract_body_content(html_content):
    """Extract conversation body as clean paragraphs."""
    parser = BodyExtractor()
    parser.feed(html_content)
    return parser.paragraphs


def extract_title(html_content):
    """Extract title from epub section."""
    m = re.search(r"<title>([^<]+)</title>", html_content)
    if m:
        t = m.group(1).strip()
    else:
        m = re.search(r'class="Heading"[^>]*>(.*?)</div>', html_content, re.DOTALL)
        if m:
            t = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
            t = re.sub(r"\s+", " ", t)
        else:
            t = "Untitled Conversation"
    # Escape for XHTML
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def extract_year(title):
    """Extract year from conversation title."""
    m = re.search(r"(\d{4})", title)
    return int(m.group(1)) if m else 0


def load_conversations():
    """Load all conversation sections from epub, sorted by section number (chronological)."""
    conversations = []
    for fname in os.listdir(EPUB_DIR):
        if not fname.startswith("section_") or not fname.endswith(".html"):
            continue
        section_num = int(fname.replace("section_", "").replace(".html", ""))
        path = os.path.join(EPUB_DIR, fname)
        with open(path, "r", errors="replace") as f:
            content = f.read()
        title = extract_title(content)
        year = extract_year(title)
        paragraphs = extract_body_content(content)
        if paragraphs:
            conversations.append({
                "section": section_num,
                "title": title,
                "year": year,
                "paragraphs": paragraphs,
            })
    conversations.sort(key=lambda c: c["section"])
    return conversations


def make_anchor(idx):
    return f"conv{idx:04d}"


def build_html(filename, title, conversations):
    """Build a single HTML file from a list of conversations."""
    # Build TOC
    toc_items = []
    for i, conv in enumerate(conversations):
        anchor = make_anchor(conv["section"])
        toc_items.append(f'<li><a href="#{anchor}">{conv["title"]}</a></li>')

    # Build content sections
    sections = []
    for conv in conversations:
        anchor = make_anchor(conv["section"])
        paras = "\n".join(f"<p>\n{p}\n</p>" for p in conv["paragraphs"])
        sections.append(
            f'<div id="outline-container-{anchor}" class="outline-2">\n'
            f'<h2 id="{anchor}">{conv["title"]}</h2>\n'
            f'<div class="outline-text-2">\n'
            f'{paras}\n'
            f'</div>\n</div>'
        )

    html = HEAD_TEMPLATE.format(title=title)
    html += "\n".join(toc_items)
    html += "\n</ul>\n</div>\n</div>\n"
    html += "\n".join(sections)
    html += FOOT_TEMPLATE

    outpath = os.path.join(OUTPUT_DIR, filename)
    with open(outpath, "w") as f:
        f.write(html)
    size_mb = os.path.getsize(outpath) / (1024 * 1024)
    print(f"  {filename}: {len(conversations)} conversations, {size_mb:.1f} MB")


def main():
    print("Loading conversations from epub...")
    conversations = load_conversations()
    print(f"  Loaded {len(conversations)} conversations")

    for filename, title, year_start, year_end in SPLITS:
        subset = [c for c in conversations if year_start <= c["year"] <= year_end]
        print(f"\nBuilding {filename} ({year_start}-{year_end})...")
        build_html(filename, title, subset)

    # Check for conversations with no year
    no_year = [c for c in conversations if c["year"] == 0]
    if no_year:
        print(f"\nWarning: {len(no_year)} conversations with no year detected:")
        for c in no_year[:5]:
            print(f"  section_{c['section']}: {c['title']}")

    print("\nDone!")


if __name__ == "__main__":
    main()
