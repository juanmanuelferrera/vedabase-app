#!/usr/bin/env python3
"""
Scrape missing conversations from Vanisource for years 1968-1976
and insert them into conv1.html (1968-1974) and conv2.html (1975-1976).
"""

import re
import time
import sys
import os
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

BASE_DIR = "/Users/jaganat/.emacs.d/git_projects/vedabase-app-website/vedabase-app/vedabase-source"
CONV1_PATH = os.path.join(BASE_DIR, "conv1.html")
CONV2_PATH = os.path.join(BASE_DIR, "conv2.html")
OUT_PRE1975 = os.path.join(BASE_DIR, "missing_convs_pre1975.html")
OUT_1975_1976 = os.path.join(BASE_DIR, "missing_convs_1975_1976.html")

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
DELAY = 0.5

MONTH_MAP = {
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'may': '05', 'june': '06', 'july': '07', 'august': '08',
    'september': '09', 'october': '10', 'november': '11', 'december': '12'
}

MONTH_NAMES = {
    '01': 'January', '02': 'February', '03': 'March', '04': 'April',
    '05': 'May', '06': 'June', '07': 'July', '08': 'August',
    '09': 'September', '10': 'October', '11': 'November', '12': 'December'
}


def fetch_url(url):
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except (URLError, HTTPError) as e:
        print(f"  ERROR fetching {url}: {e}")
        return None


def yymmdd_to_sortkey(yymmdd):
    """Convert YYMMDD to a sortable integer. 2-digit year: 60-99 = 1960-1999."""
    yy = int(yymmdd[:2])
    mm = int(yymmdd[2:4])
    dd = int(yymmdd[4:6])
    year = 1900 + yy if yy >= 60 else 2000 + yy
    return year * 10000 + mm * 100 + dd


def format_title_from_link(link, yymmdd):
    """
    Convert a Vanisource link like '720118_-_Conversation_-_Jaipur'
    into a formatted title like 'Conversation -- January 18, 1972, Jaipur'
    """
    # Remove the date prefix: 720118_-_
    rest = re.sub(r'^\d{6}_-_', '', link)
    # Replace underscores with spaces
    rest = rest.replace('_', ' ')
    # The rest is like "Conversation - Jaipur" or "Room Conversation with Bob Cohen - Bombay"
    # Find the last " - " which separates title from location
    parts = rest.rsplit(' - ', 1)
    if len(parts) == 2:
        title_part = parts[0].strip()
        location = parts[1].strip()
    else:
        title_part = rest.strip()
        location = ''

    # Format date from yymmdd
    yy = int(yymmdd[:2])
    mm = yymmdd[2:4]
    dd = int(yymmdd[4:6])
    year = 1900 + yy if yy >= 60 else 2000 + yy
    month_name = MONTH_NAMES.get(mm, mm)
    date_str = f"{month_name} {dd}, {year}"

    if location:
        return f"{title_part} -- {date_str}, {location}"
    else:
        return f"{title_part} -- {date_str}"


def get_conv_links_from_category(year):
    """Fetch category page and extract all conversation links."""
    url = f"https://vanisource.org/w/index.php?title=Category:{year}_-_Conversations&limit=500"
    print(f"Fetching category for {year}: {url}")
    html = fetch_url(url)
    if not html:
        return []

    links = re.findall(r'href="/wiki/(\d{6}[^"\'<>\s]+)"', html)
    conv_links = []
    seen = set()
    for link in links:
        if re.match(r'^\d{6}', link) and link not in seen and ':' not in link:
            conv_links.append(link)
            seen.add(link)

    print(f"  Found {len(conv_links)} conversation links for {year}")
    return conv_links


def extract_date_from_link(link):
    """Extract YYMMDD from a vanisource link like 680201_-_Conversation_..."""
    m = re.match(r'^(\d{6})', link)
    if m:
        return m.group(1)
    return None


def get_existing_dates_from_content(content):
    """
    Scan all h2 headers in a conv file content and extract all YYMMDD dates.
    Returns a set of YYMMDD strings.
    """
    h2_texts = re.findall(r'<h2[^>]*>(.*?)</h2>', content, re.DOTALL)
    dates = set()

    for h2 in h2_texts:
        clean = re.sub(r'<[^>]+>', '', h2).strip()
        # Try "Month Day, Year" pattern
        m = re.search(r'(\w+)\s+(\d{1,2}),?\s+(\d{4})', clean, re.IGNORECASE)
        if m:
            month_str = m.group(1).lower()
            day = m.group(2).zfill(2)
            year_full = m.group(3)
            year_short = year_full[2:]
            if month_str in MONTH_MAP:
                yymmdd = year_short + MONTH_MAP[month_str] + day
                dates.add(yymmdd)

        # Also try ranges like "April 5-6, 1967" -> take first date
        m2 = re.search(r'(\w+)\s+(\d{1,2})-\d{1,2},?\s+(\d{4})', clean, re.IGNORECASE)
        if m2:
            month_str = m2.group(1).lower()
            day = m2.group(2).zfill(2)
            year_full = m2.group(3)
            year_short = year_full[2:]
            if month_str in MONTH_MAP:
                yymmdd = year_short + MONTH_MAP[month_str] + day
                dates.add(yymmdd)

    return dates


def clean_html_content(html_content):
    """
    Extract and clean content from Vanisource mw-parser-output div.
    Returns cleaned HTML string.
    """
    # Find mw-parser-output start
    m = re.search(r'<div[^>]*class="mw-parser-output"[^>]*>', html_content)
    if not m:
        return None

    content = html_content[m.start():]

    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # Remove figure elements (images with captions)
    content = re.sub(r'<figure[^>]*>.*?</figure>', '', content, flags=re.DOTALL)

    # Remove img tags
    content = re.sub(r'<img[^>]*/>', '', content)
    content = re.sub(r'<img[^>]*>', '', content)

    # Remove TOC div
    content = re.sub(r'<div[^>]*id="toc"[^>]*>.*?</div>', '', content, flags=re.DOTALL)

    # Remove catlinks
    content = re.sub(r'<div[^>]*id="catlinks"[^>]*>.*?</div>', '', content, flags=re.DOTALL)

    # Remove edit section spans
    content = re.sub(r'<span[^>]*class="[^"]*mw-editsection[^"]*"[^>]*>.*?</span>', '', content, flags=re.DOTALL)

    # Remove tables (navbox, info tables)
    content = re.sub(r'<table[^>]*>.*?</table>', '', content, flags=re.DOTALL)

    # Remove script and style
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

    # Truncate at footer markers
    end_markers = [
        r'<div[^>]*class="[^"]*mw-content-footer[^"]*"',
        r'<div[^>]*id="mw-navigation"',
        r'<div[^>]*id="footer"',
    ]
    for marker in end_markers:
        m2 = re.search(marker, content)
        if m2:
            content = content[:m2.start()]
            break

    # Preserve lec_code/code divs BEFORE stripping other divs
    content = re.sub(r'<div[^>]*class="(?:lec_code|code)"[^>]*>(.*?)</div>',
                     r'<div class="code">\1</div>', content, flags=re.DOTALL)

    # Protect audio tags - mark them temporarily
    # We'll preserve <audio ...>...</audio> blocks entirely
    audio_blocks = []
    def save_audio(m):
        idx = len(audio_blocks)
        audio_blocks.append(m.group(0))
        return f'AUDIO_PLACEHOLDER_{idx}'
    content = re.sub(r'<audio[^>]*>.*?</audio>', save_audio, content, flags=re.DOTALL)

    # Now strip the navigation div at the top of mw-parser-output
    # It's a float:left div with "Conversations by Date" links
    content = re.sub(r'<div[^>]*style="float:left"[^>]*>.*?</div>', '', content, flags=re.DOTALL)
    content = re.sub(r'<div[^>]*style="float: left"[^>]*>.*?</div>', '', content, flags=re.DOTALL)

    # Strip div open/close tags (keep content)
    content = re.sub(r'<div(?:\s[^>]*)?>', '', content)
    content = re.sub(r'</div>', '', content)

    # Restore audio tags
    for idx, audio_block in enumerate(audio_blocks):
        content = content.replace(f'AUDIO_PLACEHOLDER_{idx}', audio_block)

    # Remove span tags but keep content
    content = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', content, flags=re.DOTALL)

    # Remove h1 tags (page title)
    content = re.sub(r'<h1[^>]*>.*?</h1>', '', content, flags=re.DOTALL)

    # Convert h2-h6 sub-headings to bold paragraphs
    content = re.sub(r'<h[23456][^>]*>(.*?)</h[23456]>', r'<p><b>\1</b></p>', content, flags=re.DOTALL)

    # Remove hr tags
    content = re.sub(r'<hr[^>]*/>', '', content)
    content = re.sub(r'<hr>', '', content)

    # Remove ul/li lists (categories etc)
    content = re.sub(r'<ul[^>]*>.*?</ul>', '', content, flags=re.DOTALL)

    # Strip anchor tags but keep link text
    content = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', content, flags=re.DOTALL)

    # Clean up excessive whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r'<p>\s*</p>', '', content)
    content = re.sub(r'<p>\s*<br\s*/?>\s*</p>', '', content)

    content = content.strip()
    return content


def extract_title_from_page(html_content):
    """Extract the page title from firstHeading."""
    m = re.search(r'<h1[^>]*id="firstHeading"[^>]*>.*?<span[^>]*>(.*?)</span>', html_content, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m = re.search(r'<h1[^>]*id="firstHeading"[^>]*>(.*?)</h1>', html_content, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return None


def scrape_conversation(link, yymmdd):
    """Fetch and parse a Vanisource conversation page."""
    url = f"https://vanisource.org/wiki/{link}"
    html = fetch_url(url)
    if not html:
        return None, None

    # Get title - prefer formatted version derived from link
    title = format_title_from_link(link, yymmdd)

    content = clean_html_content(html)
    if not content:
        # Try to get at least something
        raw_title = extract_title_from_page(html)
        print(f"  WARNING: Could not extract content for {link}")
        return title, ""

    return title, content


def get_max_conv_id(filepath):
    """Get the maximum conv ID number from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    ids = re.findall(r'id="conv(\d+)"', content)
    if ids:
        return max(int(x) for x in ids)
    return 0


def format_conv_block(conv_id, title, content):
    """Format a conversation as an HTML block."""
    id_str = f"conv{conv_id:04d}"
    return f'<div id="outline-container-{id_str}" class="outline-2">\n<h2 id="{id_str}">{title}</h2>\n<div class="outline-text-2">\n{content}\n</div>\n</div>\n'


def find_insertion_point_in_content(content, target_yymmdd):
    """
    Find the character position where a new conversation with target_yymmdd
    should be inserted (chronologically). Returns insert position.
    """
    target_key = yymmdd_to_sortkey(target_yymmdd)

    # Find all outline-container divs and their dates
    h2_date_pattern = re.compile(r'(\w+)\s+(\d{1,2})(?:-\d{1,2})?,?\s+(\d{4})', re.IGNORECASE)
    container_pattern = re.compile(r'<div id="outline-container-conv\d+"')

    entries = []
    for m in container_pattern.finditer(content):
        pos = m.start()
        snippet = content[pos:pos+600]
        dm = h2_date_pattern.search(snippet)
        if dm:
            month_str = dm.group(1).lower()
            day = dm.group(2).zfill(2)
            year_full = dm.group(3)
            year_short = year_full[2:]
            if month_str in MONTH_MAP:
                yymmdd = year_short + MONTH_MAP[month_str] + day
                sort_key = yymmdd_to_sortkey(yymmdd)
                entries.append((sort_key, pos))

    if not entries:
        return None

    # Find where target_key fits
    for sort_key, pos in entries:
        if target_key < sort_key:
            return pos

    # Insert before the script tag at the end
    end_patterns = [
        r'\n</div>\n</div></div>\n\n<script',
        r'\n</div>\n</div></div>\n<script',
        r'</div></div>\n\n<script',
        r'</div></div>\n<script',
    ]
    for pat in end_patterns:
        em = re.search(pat, content)
        if em:
            return em.start() + 1

    return None


def update_toc_for_new_entries(content, new_entries):
    """
    Add TOC entries for new conversations (sorted by date).
    new_entries: list of (conv_id, title, yymmdd)
    """
    toc_date_pattern = re.compile(r'(\w+)\s+(\d{1,2})(?:-\d{1,2})?,?\s+(\d{4})', re.IGNORECASE)
    toc_li_pattern = re.compile(r'<li><a href="#(conv\d+)">(.*?)</a></li>')

    # Sort new entries by date
    new_entries_sorted = sorted(new_entries, key=lambda x: yymmdd_to_sortkey(x[2]))

    for conv_id, title, yymmdd in new_entries_sorted:
        target_key = yymmdd_to_sortkey(yymmdd)
        id_str = f"conv{conv_id:04d}"
        new_toc_line = f'<li><a href="#{id_str}">{title}</a></li>'

        # Rebuild TOC entry list fresh each time (content changes)
        toc_entries = []
        for m in toc_li_pattern.finditer(content):
            dm = toc_date_pattern.search(m.group(2))
            if dm:
                month_str = dm.group(1).lower()
                day = dm.group(2).zfill(2)
                year_full = dm.group(3)
                year_short = year_full[2:]
                if month_str in MONTH_MAP:
                    yymmdd2 = year_short + MONTH_MAP[month_str] + day
                    sort_key = yymmdd_to_sortkey(yymmdd2)
                    toc_entries.append((sort_key, m.start(), m.end()))

        if not toc_entries:
            print(f"  WARNING: Could not find TOC to insert {id_str}")
            continue

        # Find insertion point
        insert_before_pos = None
        for sort_key, start, end in toc_entries:
            if target_key < sort_key:
                insert_before_pos = start
                break

        if insert_before_pos is None:
            # Insert after last TOC entry
            last_end = toc_entries[-1][2]
            content = content[:last_end] + '\n' + new_toc_line + content[last_end:]
        else:
            content = content[:insert_before_pos] + new_toc_line + '\n' + content[insert_before_pos:]

    return content


def insert_convs_into_file(filepath, scraped_list, start_id):
    """
    Insert scraped conversations into a conv HTML file chronologically.
    scraped_list: list of (yymmdd, link, title, content)
    start_id: starting conv ID number
    """
    if not scraped_list:
        print(f"  Nothing to insert into {filepath}")
        return 0, 0

    print(f"  Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_len = len(content)
    toc_additions = []
    inserted = 0
    failed = 0

    # Sort by date
    scraped_list = sorted(scraped_list, key=lambda x: yymmdd_to_sortkey(x[0]))

    for i, (yymmdd, link, title, conv_content) in enumerate(scraped_list):
        conv_id = start_id + i
        id_str = f"conv{conv_id:04d}"

        insert_pos = find_insertion_point_in_content(content, yymmdd)

        if insert_pos is None:
            print(f"    WARNING: No insertion point for {yymmdd} ({title[:50]})")
            # Try appending at very end before </body>
            em = re.search(r'<script src="font-control', content)
            if em:
                insert_pos = em.start()
            else:
                print(f"    ERROR: Cannot insert {yymmdd}, skipping")
                failed += 1
                continue

        block = format_conv_block(conv_id, title, conv_content)
        content = content[:insert_pos] + '\n' + block + content[insert_pos:]

        toc_additions.append((conv_id, title, yymmdd))
        inserted += 1

        if inserted % 20 == 0:
            print(f"    Progress: {inserted}/{len(scraped_list)} inserted...")

    print(f"  Updating TOC for {len(toc_additions)} new entries...")
    content = update_toc_for_new_entries(content, toc_additions)

    print(f"  Writing updated file...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    new_len = len(content)
    print(f"  File size: {original_len:,} -> {new_len:,} bytes (+{new_len - original_len:,})")
    return inserted, failed


def main():
    years_conv1 = [1968, 1969, 1970, 1971, 1972, 1973, 1974]
    years_conv2 = [1975, 1976]

    print("=" * 60)
    print("Loading existing dates from conv files...")
    print("=" * 60)

    with open(CONV1_PATH, 'r', encoding='utf-8') as f:
        conv1_content = f.read()
    with open(CONV2_PATH, 'r', encoding='utf-8') as f:
        conv2_content = f.read()

    existing_dates_conv1 = get_existing_dates_from_content(conv1_content)
    existing_dates_conv2 = get_existing_dates_from_content(conv2_content)

    print(f"conv1.html: {len(existing_dates_conv1)} unique dates (1967-1973)")
    print(f"conv2.html: {len(existing_dates_conv2)} unique dates (1974-1975)")

    # --- PHASE 1: Discover all missing conversations ---
    print("\n" + "=" * 60)
    print("PHASE 1: Discovering missing conversations from Vanisource")
    print("=" * 60)

    missing_conv1 = []  # list of (yymmdd, link)
    missing_conv2 = []

    for year in years_conv1 + years_conv2:
        links = get_conv_links_from_category(year)
        time.sleep(DELAY)

        if year <= 1974:
            existing_dates = existing_dates_conv1
            target_list = missing_conv1
        else:
            existing_dates = existing_dates_conv2
            target_list = missing_conv2

        year_missing = []
        for link in links:
            yymmdd = extract_date_from_link(link)
            if yymmdd and yymmdd not in existing_dates:
                target_list.append((yymmdd, link))
                year_missing.append(yymmdd)

        have_count = len(links) - len(year_missing)
        print(f"  {year}: {len(links)} on Vanisource, {have_count} already in file, {len(year_missing)} MISSING")

    print(f"\nTotal missing for conv1 (1968-1974): {len(missing_conv1)}")
    print(f"Total missing for conv2 (1975-1976): {len(missing_conv2)}")

    # Deduplicate by date (keep first occurrence per date)
    def dedup_by_date(items):
        seen = set()
        result = []
        for yymmdd, link in items:
            if yymmdd not in seen:
                seen.add(yymmdd)
                result.append((yymmdd, link))
        return result

    missing_conv1 = dedup_by_date(missing_conv1)
    missing_conv2 = dedup_by_date(missing_conv2)
    missing_conv1.sort(key=lambda x: yymmdd_to_sortkey(x[0]))
    missing_conv2.sort(key=lambda x: yymmdd_to_sortkey(x[0]))

    print(f"After dedup - conv1: {len(missing_conv1)}, conv2: {len(missing_conv2)}")

    # --- PHASE 2: Scrape missing conversations ---
    print("\n" + "=" * 60)
    print("PHASE 2: Scraping conversation content from Vanisource")
    print("=" * 60)

    def scrape_batch(missing_list, label):
        results = []
        total = len(missing_list)
        for i, (yymmdd, link) in enumerate(missing_list, 1):
            print(f"  [{i}/{total}] {label} {yymmdd}: {link[:70]}")
            title, conv_content = scrape_conversation(link, yymmdd)
            if title is not None:
                results.append((yymmdd, link, title, conv_content))
                print(f"    -> {title[:80]}")
            else:
                print(f"    -> FAILED, skipping")
            time.sleep(DELAY)
        return results

    print(f"\nScraping {len(missing_conv1)} conversations for conv1 (1968-1974)...")
    scraped_conv1 = scrape_batch(missing_conv1, "conv1")

    print(f"\nScraping {len(missing_conv2)} conversations for conv2 (1975-1976)...")
    scraped_conv2 = scrape_batch(missing_conv2, "conv2")

    print(f"\nSuccessfully scraped: conv1={len(scraped_conv1)}, conv2={len(scraped_conv2)}")

    # --- PHASE 3: Save intermediate files ---
    print("\n" + "=" * 60)
    print("PHASE 3: Saving intermediate files")
    print("=" * 60)

    def save_intermediate(scraped, filepath, start_id):
        if not scraped:
            print(f"  No content for {filepath}")
            return
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, (yymmdd, link, title, conv_content) in enumerate(scraped):
                conv_id = start_id + i
                block = format_conv_block(conv_id, title, conv_content)
                f.write(block)
                f.write('\n')
        print(f"  Saved {len(scraped)} conversations to {os.path.basename(filepath)}")

    # Use ID ranges that won't conflict within each file
    # conv1 currently: 102-342 (212 entries). New entries: start at 9000.
    # conv2 currently: 243-756 (408 entries). New entries: start at 9500.
    save_intermediate(scraped_conv1, OUT_PRE1975, 9000)
    save_intermediate(scraped_conv2, OUT_1975_1976, 9500)

    # --- PHASE 4: Insert into conv files ---
    print("\n" + "=" * 60)
    print("PHASE 4: Inserting into conv HTML files")
    print("=" * 60)

    print("\nInserting into conv1.html...")
    ins1, fail1 = insert_convs_into_file(CONV1_PATH, scraped_conv1, 9000)

    print("\nInserting into conv2.html...")
    ins2, fail2 = insert_convs_into_file(CONV2_PATH, scraped_conv2, 9500)

    # --- SUMMARY ---
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    for fname in ['conv1.html', 'conv2.html', 'conv3.html']:
        path = os.path.join(BASE_DIR, fname)
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read()
        count = len(re.findall(r'<h2 id="conv', c))
        print(f"  {fname}: {count} conversations total")

    print(f"\n  conv1: inserted={ins1}, failed={fail1}")
    print(f"  conv2: inserted={ins2}, failed={fail2}")
    print(f"\n  Intermediate files:")
    for fname in [OUT_PRE1975, OUT_1975_1976]:
        if os.path.exists(fname):
            size = os.path.getsize(fname)
            print(f"    {os.path.basename(fname)}: {size:,} bytes")
    print("\nDone!")


if __name__ == '__main__':
    main()
