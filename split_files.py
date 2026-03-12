#!/usr/bin/env python3
"""
Split large HTML files into smaller parts for better loading performance.
"""

import os
import sys

def read_header_footer(filepath, header_lines=100, footer_lines=20):
    """Read the HTML header and footer structures."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    header = ''.join(lines[:header_lines])
    footer = ''.join(lines[-footer_lines:])

    return header, footer, lines

def split_sb_html():
    """Split Srimad-Bhagavatam into 3 parts by Cantos."""
    filepath = 'vedabase-app/vedabase-source/sb.html'
    print(f"Splitting {filepath}...")

    header, footer, all_lines = read_header_footer(filepath)

    # Split points based on Canto boundaries
    # Part 1: Cantos 1-3 (lines 1 to 79,290)
    # Part 2: Cantos 4-7 (lines 79,291 to 322,318)
    # Part 3: Cantos 8-10 (lines 322,319 to end)

    splits = [
        ('sb1.html', 1, 79290, 'Cantos 1-3'),
        ('sb2.html', 79291, 322318, 'Cantos 4-7'),
        ('sb3.html', 322319, None, 'Cantos 8-10')
    ]

    for filename, start, end, description in splits:
        output_path = f'vedabase-app/vedabase-source/{filename}'
        print(f"  Creating {filename} ({description})...")

        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(header)

            # Write content slice (adjust for 0-based indexing)
            if end is None:
                content_lines = all_lines[start-1:]
            else:
                content_lines = all_lines[start-1:end]

            # Find where to cut off before footer in content
            # Skip the header part and write middle content
            for i, line in enumerate(content_lines):
                # Skip header lines if this is not the first part
                if start > 1 and i < 100:
                    continue
                f.write(line)

            # Write footer
            f.write(footer)

        # Get file size
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"    ✓ Created {filename} ({size_mb:.1f} MB)")

    print(f"  ✓ Srimad-Bhagavatam split complete\n")

def split_cc_html():
    """Split Caitanya Caritamrta into 2 parts by Lilas."""
    filepath = 'vedabase-app/vedabase-source/cc.html'
    print(f"Splitting {filepath}...")

    # First, find the split points by searching for Lilas
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    middle = total_lines // 2

    header, footer, all_lines = read_header_footer(filepath)

    splits = [
        ('cc1.html', 1, middle, 'Part 1'),
        ('cc2.html', middle + 1, None, 'Part 2')
    ]

    for filename, start, end, description in splits:
        output_path = f'vedabase-app/vedabase-source/{filename}'
        print(f"  Creating {filename} ({description})...")

        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(header)

            # Write content slice
            if end is None:
                content_lines = all_lines[start-1:]
            else:
                content_lines = all_lines[start-1:end]

            for i, line in enumerate(content_lines):
                if start > 1 and i < 100:
                    continue
                f.write(line)

            # Write footer
            f.write(footer)

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"    ✓ Created {filename} ({size_mb:.1f} MB)")

    print(f"  ✓ Caitanya Caritamrta split complete\n")

def split_lec_html(filename_base):
    """Split lecture files into 3 parts by line count."""
    filepath = f'vedabase-app/vedabase-source/{filename_base}.html'
    print(f"Splitting {filepath}...")

    header, footer, all_lines = read_header_footer(filepath)
    total_lines = len(all_lines)

    # Split into 3 roughly equal parts
    part_size = total_lines // 3

    splits = [
        (f'{filename_base}a.html', 1, part_size, 'Part 1'),
        (f'{filename_base}b.html', part_size + 1, part_size * 2, 'Part 2'),
        (f'{filename_base}c.html', part_size * 2 + 1, None, 'Part 3')
    ]

    for filename, start, end, description in splits:
        output_path = f'vedabase-app/vedabase-source/{filename}'
        print(f"  Creating {filename} ({description})...")

        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(header)

            # Write content slice
            if end is None:
                content_lines = all_lines[start-1:]
            else:
                content_lines = all_lines[start-1:end]

            for i, line in enumerate(content_lines):
                if start > 1 and i < 100:
                    continue
                f.write(line)

            # Write footer
            f.write(footer)

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"    ✓ Created {filename} ({size_mb:.1f} MB)")

    print(f"  ✓ {filename_base} split complete\n")

def main():
    print("Starting file splitting...\n")

    # Split Srimad-Bhagavatam
    split_sb_html()

    # Split Caitanya Caritamrta
    split_cc_html()

    # Split Lectures 1
    split_lec_html('lec1')

    # Split Lectures 2
    split_lec_html('lec2')

    print("\n✓ All files split successfully!")

if __name__ == '__main__':
    main()
