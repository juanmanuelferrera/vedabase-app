#!/usr/bin/env python3
"""
Split Srimad-Bhagavatam at Canto boundaries with proper div closing.
"""

import os

def split_sb_at_cantos():
    """Split SB at exact Canto header lines with proper HTML structure."""
    filepath = 'sb.html'
    print(f"Splitting {filepath} at Canto boundaries...")

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total lines: {total_lines}")

    # Extract header (first 100 lines)
    header_end = 100
    header = lines[:header_end]

    # Find the proper footer - the last part with closing divs and postamble
    # This is approximately the last 25 lines
    footer_start = total_lines - 25
    footer = lines[footer_start:]

    # The content wrapper needs 1 closing </div> for #content div
    # Based on the structure, after each Canto section ends, there are 4 closing </div> tags
    # But we need to add 1 more </div> to close the #content div
    content_close = '</div>\n'

    # Split points (0-indexed):
    # sb1 ends at line 154449 (after "END OF THE THIRD CANTO" and its 4 closing divs)
    # sb2 starts at line 154450 (the <div> that contains Fourth Canto)
    # sb2 ends at line 367588 (after Seventh Canto ends and its 4 closing divs)
    # sb3 starts at line 367589 (the <div> that contains Eighth Canto)

    splits = [
        ('sb1.html', 0, 154449, 'Cantos 1-3', True),
        ('sb2.html', 154450, 367588, 'Cantos 4-7', False),
        ('sb3.html', 367589, footer_start, 'Cantos 8-10', False)
    ]

    for i, (filename, start_idx, end_idx, description, is_first) in enumerate(splits):
        print(f"  Creating {filename} ({description})...")

        with open(filename, 'w', encoding='utf-8') as f:
            if is_first:
                # First part: includes original header, write content as-is
                f.writelines(lines[start_idx:end_idx])
                # Add one more closing div for the content wrapper
                f.write(content_close)
            else:
                # Subsequent parts: need to add header and open content div
                f.writelines(header)
                # Re-open the content div structure that was in the original header
                # This is already in the header, so just write the content
                f.writelines(lines[start_idx:end_idx])
                # Add closing div for content wrapper
                f.write(content_close)

            # Add footer to all parts
            f.writelines(footer)

        size_mb = os.path.getsize(filename) / (1024 * 1024)
        line_count = end_idx - start_idx
        print(f"    ✓ Created {filename} ({size_mb:.1f} MB, {line_count:,} lines)")

    print(f"  ✓ Srimad-Bhagavatam split complete\n")

if __name__ == '__main__':
    split_sb_at_cantos()
