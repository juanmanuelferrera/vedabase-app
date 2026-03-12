#!/usr/bin/env python3
"""
Split Srimad-Bhagavatam at Canto boundaries - properly indexed.
"""

import os

def split_sb_at_cantos():
    """Split SB at exact Canto div boundaries."""
    filepath = 'sb.html'
    print(f"Splitting {filepath} at Canto boundaries...")

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total lines: {total_lines}")

    # Extract header (first 100 lines)
    header_end = 100
    header = lines[:header_end]

    # Footer (last 25 lines)
    footer_start = total_lines - 25
    footer = lines[footer_start:]

    # One closing div for the content wrapper
    content_close = '</div>\n'

    # Adjusted split points (0-indexed):
    # Line 154449 in text editor = index 154448 in 0-indexed array
    # That line is: <div id="outline-container-orgce6e332" class="outline-2">
    # So sb1 should end at index 154447 (line 154448 in editor)
    # sb2 should start at index 154448 (line 154449 in editor)

    splits = [
        ('sb1.html', 0, 154448, 'Cantos 1-3', True),
        ('sb2.html', 154448, 367587, 'Cantos 4-7', False),
        ('sb3.html', 367587, footer_start, 'Cantos 8-10', False)
    ]

    for i, (filename, start_idx, end_idx, description, is_first) in enumerate(splits):
        print(f"  Creating {filename} ({description})...")

        with open(filename, 'w', encoding='utf-8') as f:
            if is_first:
                # First part: write as-is from start
                f.writelines(lines[start_idx:end_idx])
                # Add closing div for content
                f.write(content_close)
            else:
                # Add header
                f.writelines(header)
                # Write content from split point
                f.writelines(lines[start_idx:end_idx])
                # Add closing div for content
                f.write(content_close)

            # Add footer
            f.writelines(footer)

        size_mb = os.path.getsize(filename) / (1024 * 1024)
        line_count = end_idx - start_idx
        print(f"    ✓ Created {filename} ({size_mb:.1f} MB, {line_count:,} lines)")

    print(f"  ✓ Srimad-Bhagavatam split complete\n")

if __name__ == '__main__':
    split_sb_at_cantos()
