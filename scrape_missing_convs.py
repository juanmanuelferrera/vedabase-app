#!/usr/bin/env python3
"""Scrape missing 1977 conversations from Vanisource and add to conv3.html"""

import re
import urllib.request
import time
import html
import os

BASE = "/Users/jaganat/.emacs.d/git_projects/vedabase-app-website/vedabase-app/vedabase-source"
VANISOURCE = "https://vanisource.org"

MONTHS = {'01':'January','02':'February','03':'March','04':'April','05':'May','06':'June',
          '07':'July','08':'August','09':'September','10':'October','11':'November','12':'December'}


def get_our_dates():
    """Get all 1977 conversation dates we already have."""
    dates = set()
    for f in ['conv1.html', 'conv2.html', 'conv3.html']:
        path = os.path.join(BASE, f)
        with open(path) as fh:
            content = fh.read()
        for m in re.finditer(r'<h2[^>]*>([^<]*1977[^<]*)</h2>', content):
            title = m.group(1)
            date_match = re.search(r'(\w+ \d+(?:-\d+)?), 1977', title)
            if date_match:
                dates.add(date_match.group(1) + ', 1977')
    return dates


def get_vanisource_links():
    """Get all 1977 conversation links from Vanisource."""
    url = f'{VANISOURCE}/w/index.php?title=Category:1977_-_Conversations&limit=500'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html_content = urllib.request.urlopen(req).read().decode('utf-8')
    links = re.findall(r'/wiki/(77\d{4}_-_Conversation[^"]*)', html_content)
    return links


def get_missing_links(our_dates, all_links):
    """Find which Vanisource links we're missing."""
    missing = []
    for link in all_links:
        date_code = link[:6]
        month = MONTHS[date_code[2:4]]
        day = str(int(date_code[4:6]))
        date_str = f'{month} {day}, 1977'
        if date_str not in our_dates:
            missing.append(link)
    return missing


def fetch_conversation(link):
    """Fetch a single conversation from Vanisource and extract the text."""
    url = f'{VANISOURCE}/wiki/{link}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        raw = urllib.request.urlopen(req).read().decode('utf-8')
    except Exception as e:
        print(f"  ERROR fetching {link}: {e}")
        return None, None

    # Extract title from the page
    title_match = re.search(r'<h1[^>]*id="firstHeading"[^>]*>([^<]+)</h1>', raw)
    if not title_match:
        title_match = re.search(r'<title>([^<]+)</title>', raw)
    title = title_match.group(1).strip() if title_match else link.replace('_', ' ')
    # Clean up title - remove " - Vanisource" suffix
    title = re.sub(r'\s*-\s*Vanisource.*', '', title)
    # Convert date code to readable: "770214 - Conversation - Mayapur" -> proper title
    title = title.replace('_', ' ')

    # Extract the main content
    content_match = re.search(r'<div id="mw-content-text"[^>]*>(.*?)</div>\s*<!--', raw, re.DOTALL)
    if not content_match:
        content_match = re.search(r'class="mw-parser-output">(.*?)</div>\s*<div', raw, re.DOTALL)
    if not content_match:
        print(f"  WARNING: Could not extract content from {link}")
        return title, None

    content = content_match.group(1)

    # Clean up the content
    # Remove edit links, categories, etc.
    content = re.sub(r'<span class="mw-editsection">.*?</span>', '', content, flags=re.DOTALL)
    content = re.sub(r'<div class="catlinks.*?</div>', '', content, flags=re.DOTALL)
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    # Remove table of contents
    content = re.sub(r'<div id="toc".*?</div>\s*</div>', '', content, flags=re.DOTALL)
    # Remove navigation links at bottom
    content = re.sub(r'<div class="nav.*?</div>', '', content, flags=re.DOTALL)

    # Keep only meaningful content (paragraphs, bold for speaker names)
    # Strip most HTML but keep <p>, <b>, <br>
    content = re.sub(r'<div[^>]*>', '', content)
    content = re.sub(r'</div>', '', content)
    content = content.strip()

    return title, content


def format_title(link):
    """Convert Vanisource link to a readable title."""
    # 770214_-_Conversation_A_-_Mayapur -> Conversation -- February 14, 1977, Mayapur
    parts = link.replace('_', ' ').split(' - ')
    date_code = parts[0].strip()  # 770214

    month = MONTHS[date_code[2:4]]
    day = str(int(date_code[4:6]))

    if len(parts) >= 3:
        conv_type = parts[1].strip()  # "Conversation A" or "Conversation"
        location = parts[2].strip()
        return f"{conv_type}--{month} {day}, 1977, {location}"
    elif len(parts) >= 2:
        conv_type = parts[1].strip()
        return f"{conv_type}--{month} {day}, 1977"
    else:
        return f"Conversation--{month} {day}, 1977"


def main():
    print("Getting our existing conversation dates...")
    our_dates = get_our_dates()
    print(f"  We have {len(our_dates)} unique dates in 1977")

    print("Getting Vanisource conversation links...")
    all_links = get_vanisource_links()
    print(f"  Vanisource has {len(all_links)} conversations in 1977")

    missing = get_missing_links(our_dates, all_links)
    print(f"  Missing: {len(missing)} conversations")

    if not missing:
        print("Nothing to do!")
        return

    # Read current conv3.html to find where to insert
    conv3_path = os.path.join(BASE, 'conv3.html')
    with open(conv3_path) as f:
        conv3 = f.read()

    # Find the insertion point - after conv1127 (last Jan 1977) and before conv1333 (Oct 1977)
    # We'll insert before the Oct 1977 section
    insert_marker = '<h2 id="conv1333">'
    if insert_marker not in conv3:
        print(f"ERROR: Cannot find insertion point '{insert_marker}' in conv3.html")
        return

    new_entries = []
    conv_id = 1128  # Start numbering after conv1127

    for i, link in enumerate(missing):
        title = format_title(link)
        print(f"  [{i+1}/{len(missing)}] Fetching: {title}")

        page_title, content = fetch_conversation(link)
        if content is None:
            print(f"    Skipping (no content)")
            continue

        entry = f'\n<h2 id="conv{conv_id:04d}">{title}</h2>\n{content}\n'
        new_entries.append(entry)
        conv_id += 1

        # Rate limit
        time.sleep(0.5)

        # Progress
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i+1}/{len(missing)} fetched")

    print(f"\nFetched {len(new_entries)} conversations")

    # Insert into conv3.html
    insert_pos = conv3.index(insert_marker)
    new_conv3 = conv3[:insert_pos] + '\n'.join(new_entries) + '\n' + conv3[insert_pos:]

    with open(conv3_path, 'w') as f:
        f.write(new_conv3)

    print(f"Updated conv3.html with {len(new_entries)} new conversations")

    # Also update the table of contents if there is one
    # Update the TXT source files too
    print("\nDone! Remember to:")
    print("1. Update the service worker cache version")
    print("2. Sync deploy/app/ with vedabase-app/")
    print("3. Redeploy")


if __name__ == '__main__':
    main()
