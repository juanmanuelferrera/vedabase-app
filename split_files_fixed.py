#!/usr/bin/env python3
"""
Split large HTML files into smaller parts for better loading performance.
"""

import os
import re

def split_sb_html():
    """Split Srimad-Bhagavatam into 3 parts by Cantos."""
    filepath = 'vedabase-app/vedabase-source/sb.html'
    print(f"Splitting {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find where the body content starts (after </head><body>)
    body_start = content.find('</head>') + len('</head>')
    header = content[:body_start]

    # Find where the body ends (before </body></html>)
    body_end = content.rfind('</div>\n<div id="postamble"')
    footer = content[body_end:]

    # Get just the content between header and footer
    body_content = content[body_start:body_end]

    # Split points based on line positions in original file
    # We need to find these in the actual content
    splits = [
        ('sb1.html', 0, 79290, 'Cantos 1-3'),
        ('sb2.html', 79290, 322318, 'Cantos 4-7'),
        ('sb3.html', 322318, None, 'Cantos 8-10')
    ]

    # Split by character count approximation (lines * ~100 chars per line)
    # But we'll use the full file and split it properly
    with open(filepath, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    for filename, start_line, end_line, description in splits:
        output_path = f'vedabase-app/vedabase-source/{filename}'
        print(f"  Creating {filename} ({description})...")

        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header (first 100 lines)
            f.writelines(all_lines[:100])

            # Write content slice
            if end_line is None:
                content_lines = all_lines[start_line:]
            else:
                content_lines = all_lines[start_line:end_line]

            f.writelines(content_lines)

            # Write footer (last 20 lines)
            f.writelines(all_lines[-20:])

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"    ✓ Created {filename} ({size_mb:.1f} MB)")

    print(f"  ✓ Srimad-Bhagavatam split complete\n")

def split_file_simple(input_file, output_prefix, num_parts, description):
    """Split a file into equal parts."""
    print(f"Splitting {input_file}...")

    with open(input_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    total_lines = len(all_lines)

    # Determine header and footer
    header_end = 100  # First 100 lines are header
    footer_start = total_lines - 20  # Last 20 lines are footer

    # Content is between header and footer
    content_start = header_end
    content_end = footer_start
    content_lines = all_lines[content_start:content_end]

    part_size = len(content_lines) // num_parts

    suffixes = ['a', 'b', 'c', 'd', 'e'][:num_parts]

    for i, suffix in enumerate(suffixes):
        filename = f'{output_prefix}{suffix}.html'
        output_path = f'vedabase-app/vedabase-source/{filename}'
        print(f"  Creating {filename} (Part {i+1})...")

        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.writelines(all_lines[:header_end])

            # Write content slice
            if i == len(suffixes) - 1:
                # Last part gets everything remaining
                f.writelines(content_lines[i * part_size:])
            else:
                f.writelines(content_lines[i * part_size:(i + 1) * part_size])

            # Write footer
            f.writelines(all_lines[footer_start:])

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"    ✓ Created {filename} ({size_mb:.1f} MB)")

    print(f"  ✓ {description} split complete\n")

def main():
    print("Starting file splitting...\n")

    # Split Srimad-Bhagavatam
    split_sb_html()

    # Split Caitanya Caritamrta
    split_file_simple('vedabase-app/vedabase-source/cc.html', 'cc', 2, 'Caitanya Caritamrta')

    # Split Lectures 1
    split_file_simple('vedabase-app/vedabase-source/lec1.html', 'lec1', 3, 'Lectures 1')

    # Split Lectures 2
    split_file_simple('vedabase-app/vedabase-source/lec2.html', 'lec2', 3, 'Lectures 2')

    print("\n✓ All files split successfully!")

if __name__ == '__main__':
    main()
