#!/usr/bin/env python3
"""
Split Caitanya Caritamrta at Līlā boundaries - properly indexed.
"""

import os

def split_cc_at_lilas():
    """Split CC at exact Līlā div boundaries."""
    filepath = 'cc.html'
    print(f"Splitting {filepath} at Līlā boundaries...")

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total lines: {total_lines}")

    # Extract header with TOC (up to line 222, includes TOC but excludes Preface/Introduction)
    header_with_toc = 222
    header = lines[:header_with_toc]

    # Footer starts at postamble (line 607579, index 607578)
    footer_start = 607578
    footer = lines[footer_start:]

    # For Adi-lila, start content after TOC, Preface, and Introduction
    # Find where Adi-lila actual content starts (after introduction ends)
    adi_content_start = 1157  # Line 1157 where Adi-lila div opens

    # One closing div for the content wrapper
    content_close = '</div>\n'

    # Adjusted split points (0-indexed):
    # Line 129137 in editor = index 129136 where Madhya-lila div opens
    # cc1 should end at index 129136 (before Madhya-lila opening div)
    # Line 447753 in editor = index 447752 where Antya-lila div opens
    # cc2 should end at index 447752 (before Antya-lila opening div)

    splits = [
        ('cc1.html', adi_content_start, 129136, 'Ādi-līlā', False),
        ('cc2.html', 129137, 447752, 'Madhya-līlā', False),
        ('cc3.html', 447753, 607576, 'Antya-līlā', False)  # Include 3 closing divs (lines 607574-607576)
    ]

    for i, (filename, start_idx, end_idx, description, is_first) in enumerate(splits):
        print(f"  Creating {filename} ({description})...")

        with open(filename, 'w', encoding='utf-8') as f:
            # All files use the same structure: header + content + content_close + footer
            # Add header with TOC (but no Preface/Introduction)
            f.writelines(header)
            # Write content starting from the Lila
            f.writelines(lines[start_idx:end_idx])
            # Always add closing div for content wrapper opened in header
            f.write(content_close)
            # Add footer (postamble only, not content closing divs)
            f.writelines(footer)

        size_mb = os.path.getsize(filename) / (1024 * 1024)
        line_count = end_idx - start_idx
        print(f"    ✓ Created {filename} ({size_mb:.1f} MB, {line_count:,} lines)")

    print(f"  ✓ Caitanya Caritāmṛta split complete\n")

if __name__ == '__main__':
    split_cc_at_lilas()
