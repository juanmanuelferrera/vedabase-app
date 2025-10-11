#!/usr/bin/env python3
"""
Split Srimad-Bhagavatam at Canto boundaries.
"""

import os

def split_sb_at_cantos():
    """Split SB at exact Canto header lines."""
    filepath = 'sb.html'
    print(f"Splitting {filepath} at Canto boundaries...")

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total lines: {total_lines}")

    # Find the footer (last ~20 lines with closing tags)
    footer_start = total_lines - 20
    footer = lines[footer_start:]

    # Split points (line numbers are 1-indexed, but list is 0-indexed)
    # Line 154450 is index 154449
    # Line 367589 is index 367588
    splits = [
        ('sb1.html', 0, 154449, 'Cantos 1-3'),
        ('sb2.html', 154449, 367588, 'Cantos 4-7'),
        ('sb3.html', 367588, footer_start, 'Cantos 8-10')
    ]

    for filename, start_idx, end_idx, description in splits:
        print(f"  Creating {filename} ({description})...")

        with open(filename, 'w', encoding='utf-8') as f:
            # Write content from start to end
            f.writelines(lines[start_idx:end_idx])

            # Add footer
            f.writelines(footer)

        size_mb = os.path.getsize(filename) / (1024 * 1024)
        line_count = end_idx - start_idx
        print(f"    ✓ Created {filename} ({size_mb:.1f} MB, {line_count:,} lines)")

    print(f"  ✓ Srimad-Bhagavatam split complete\n")

if __name__ == '__main__':
    split_sb_at_cantos()
