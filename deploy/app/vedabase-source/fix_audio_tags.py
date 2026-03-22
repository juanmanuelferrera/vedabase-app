#!/usr/bin/env python3
"""
Fix two issues in newly added conversations (conv IDs 9000+):
1. Orphaned <source> tags that should be wrapped in <audio controls="">...</audio>
2. lec_code content not wrapped in <div class="code">
"""

import re
import os

BASE_DIR = "/Users/jaganat/.emacs.d/git_projects/vedabase-app-website/vedabase-app/vedabase-source"

def fix_orphaned_sources(content):
    """
    Fix orphaned <source src="..." type="audio/mpeg" /></audio> patterns.
    These should be: <audio controls=""><source src="..." type="audio/mpeg" /></audio>
    """
    # Pattern: <source src="...mp3..." .../></audio>  (orphaned, missing <audio> opener)
    # Sometimes appears as: <source src="..." type="audio/mpeg" /></audio>
    count = 0

    def fix_source(m):
        nonlocal count
        count += 1
        return f'<audio controls="">{m.group(0)}'

    # Match <source ...> followed by </audio> (the </audio> was already there as a closing tag
    # from when the <audio> wrapper was stripped)
    new_content = re.sub(r'(?<!<audio controls="">)(<source\s+src="[^"]*\.mp3"[^>]*/></audio>)', fix_source, content)

    return new_content, count


def fix_lec_code(content):
    """
    Fix lec_code content - these strings like "680506R1-BOSTON - May 06, 1968 - 09:51 Minutes"
    appear as plain text and should be wrapped in <div class="code">...</div>
    """
    # Pattern: a line that looks like "YYMMDDXY-LOCATION - Month DD, YYYY - HH:MM Minutes"
    # These appear at start of outline-text-2 divs after the newline
    pattern = r'(\n)((\d{6}[A-Z0-9]+-[A-Z]+(?:\d+)?(?:-[A-Z]+)* - [A-Za-z]+ \d{2}, \d{4} - \d+:\d+ Minutes))'
    count = 0

    def fix_code(m):
        nonlocal count
        count += 1
        return f'{m.group(1)}<div class="code">{m.group(3)}</div>'

    new_content = re.sub(pattern, fix_code, content)
    return new_content, count


def fix_file(filepath, min_id=9000):
    """Fix audio and lec_code issues only in entries with IDs >= min_id."""
    print(f"Processing {os.path.basename(filepath)}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_len = len(content)

    # Fix 1: Orphaned source tags
    # These appear as: <source src="...mp3..." /></audio>
    # We need to add <audio controls=""> before them

    # Count before
    before_audio = content.count('<audio')
    before_source = content.count('<source')

    # Fix orphaned sources: find <source ...mp3... /></audio> not preceded by <audio
    # Strategy: replace </audio> that comes right after </source> tag (no opening <audio>)
    # Actually simpler: find every <source src="*.mp3" .../></audio> and ensure it has <audio> before

    fixed_audio = 0

    def fix_orphan(m):
        nonlocal fixed_audio
        fixed_audio += 1
        return f'<audio controls="">{m.group(1)}</audio>'

    # Pattern: <source src="...mp3..." .../> followed immediately by </audio>
    # The .* is non-greedy to match just the source tag
    content = re.sub(
        r'<source\s+src="([^"]*\.mp3)"([^>]*)/>[ \t]*</audio>',
        lambda m: f'<audio controls=""><source src="{m.group(1)}"{m.group(2)}/></audio>',
        content
    )

    after_audio = content.count('<audio')
    fixed_audio = after_audio - before_audio
    print(f"  Audio tags: {before_audio} -> {after_audio} (+{fixed_audio} added)")

    # Fix 2: lec_code text not wrapped in div
    # These appear as raw text like "680506R1-BOSTON - May 06, 1968 - 09:51 Minutes"
    # right after the <div class="outline-text-2"> open tag

    before_code = content.count('<div class="code">')

    # Match the lec_code pattern: YYMMDDX-LOCATION - Month DD, YYYY - MM:SS Minutes
    # It appears as: \n680506R1-BOSTON - May 06, 1968 - 09:51 Minutes\n
    # We need to wrap it: \n<div class="code">680506R1-BOSTON - May 06, 1968 - 09:51 Minutes</div>\n
    content = re.sub(
        r'\n(\d{6}[A-Z0-9]+-[A-Z][A-Z0-9\-]*\s+-\s+[A-Za-z]+ \d{2}, \d{4}\s+-\s+\d+:\d+ Minutes)\n',
        r'\n<div class="code">\1</div>\n',
        content
    )

    after_code = content.count('<div class="code">')
    fixed_code = after_code - before_code
    print(f"  Code divs: {before_code} -> {after_code} (+{fixed_code} added)")

    new_len = len(content)
    print(f"  File size: {original_len:,} -> {new_len:,} bytes (+{new_len - original_len:,})")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return fixed_audio, fixed_code


def main():
    files = [
        os.path.join(BASE_DIR, "conv1.html"),
        os.path.join(BASE_DIR, "conv2.html"),
        os.path.join(BASE_DIR, "missing_convs_pre1975.html"),
        os.path.join(BASE_DIR, "missing_convs_1975_1976.html"),
    ]

    total_audio = 0
    total_code = 0

    for filepath in files:
        if os.path.exists(filepath):
            fa, fc = fix_file(filepath)
            total_audio += fa
            total_code += fc
            print()

    print(f"Total: {total_audio} audio tags fixed, {total_code} code divs added")

    # Verify
    print("\nVerification:")
    for fname in ['conv1.html', 'conv2.html']:
        path = os.path.join(BASE_DIR, fname)
        with open(path) as f:
            c = f.read()
        audio = c.count('<audio')
        source = c.count('<source')
        orphan = source - audio  # Each audio tag has one source inside it
        code = c.count('<div class="code">')
        h2 = c.count('<h2 id=')
        print(f"  {fname}: {h2} entries, {audio} audio tags, {orphan} orphaned sources, {code} code divs")


if __name__ == '__main__':
    main()
