#!/usr/bin/env python3
"""
Split Srimad-Bhagavatam at Canto boundaries with proper header and footer.
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

    # Extract header including TOC (up to line 8840, after org100562c closes)
    header_end = 8840
    header = lines[:header_end]

    # Footer starts at postamble (line 496113, index 496112)
    footer_start = 496112
    footer = lines[footer_start:]

    # One closing div for the content wrapper
    content_close = '</div>\n'

    # Split points (0-indexed):
    # sb1: 0 to 154443 (end of Third Canto including its 4 closing divs)
    # sb2: 154448 to 367584 (Fourth to Seventh Canto, before Eighth Canto div)
    # sb3: 367585 to footer_start (Eighth to Tenth Canto)

    splits = [
        ('sb1.html', 0, 154443, 'Cantos 1-3', True),
        ('sb2.html', 154448, 367584, 'Cantos 4-7', False),
        ('sb3.html', 367585, footer_start, 'Cantos 8-10', False)
    ]

    for i, (filename, start_idx, end_idx, description, is_first) in enumerate(splits):
        print(f"  Creating {filename} ({description})...")
        is_last = (i == len(splits) - 1)

        with open(filename, 'w', encoding='utf-8') as f:
            if is_first:
                # First part: write as-is from start (includes natural header)
                f.writelines(lines[start_idx:end_idx])
                # Add closing div for content
                f.write(content_close)
            else:
                # Add full header (includes TOC)
                f.writelines(header)
                # Write content from split point
                f.writelines(lines[start_idx:end_idx])
                # Add closing div for content (unless last part which already has closing divs)
                if not is_last:
                    f.write(content_close)

            # Add footer (postamble only, not content closing divs)
            f.writelines(footer)

        size_mb = os.path.getsize(filename) / (1024 * 1024)
        line_count = end_idx - start_idx
        print(f"    ✓ Created {filename} ({size_mb:.1f} MB, {line_count:,} lines)")

    print(f"  ✓ Srimad-Bhagavatam split complete\n")

if __name__ == '__main__':
    split_sb_at_cantos()
