#!/usr/bin/env python3
"""
Split large HTML files properly by extracting header, content sections, and footer.
"""

import os
import re

def extract_header_footer(filepath):
    """Extract the header and footer from an HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the actual content start (after </head><body> and initial divs)
    # Look for the first substantial content after the header
    header_match = re.search(r'(<\?xml.*?</head>\s*<body>.*?<div[^>]*>\s*<h1[^>]*>.*?</h1>)', content, re.DOTALL)

    if not header_match:
        # Fallback: just use first 200 lines
        lines = content.split('\n')
        header = '\n'.join(lines[:200])
        content_start_pos = len(header)
    else:
        header = header_match.group(1)
        content_start_pos = header_match.end()

    # Find footer (starts with closing divs and postamble)
    footer_match = re.search(r'(</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*<div id="postamble".*?</html>)', content, re.DOTALL)

    if not footer_match:
        # Fallback
        lines = content.split('\n')
        footer = '\n'.join(lines[-30:])
        content_end_pos = len(content) - len(footer)
    else:
        footer = footer_match.group(1)
        content_end_pos = footer_match.start()

    # Get the actual content between header and footer
    main_content = content[content_start_pos:content_end_pos]

    return header, main_content, footer

def split_file(input_file, output_prefix, num_parts, part_names):
    """Split a file into parts."""
    print(f"Splitting {input_file}...")

    header, content, footer = extract_header_footer(input_file)

    # Split content into roughly equal parts
    content_length = len(content)
    part_size = content_length // num_parts

    for i, part_name in enumerate(part_names):
        output_file = f'vedabase-app/vedabase-source/{output_prefix}{part_name}.html'
        print(f"  Creating {output_prefix}{part_name}.html...")

        # Calculate start and end positions
        start_pos = i * part_size
        if i == num_parts - 1:
            # Last part gets everything remaining
            end_pos = content_length
        else:
            end_pos = (i + 1) * part_size

        part_content = content[start_pos:end_pos]

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write('\n')
            f.write(part_content)
            f.write('\n')
            f.write(footer)

        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"    ✓ Created {output_prefix}{part_name}.html ({size_mb:.1f} MB)")

def main():
    print("Starting file splitting...\n")

    # Split Srimad-Bhagavatam into 3 parts
    split_file('vedabase-app/vedabase-source/sb.html', 'sb', 3, ['1', '2', '3'])

    # Split Caitanya Caritamrta into 2 parts
    split_file('vedabase-app/vedabase-source/cc.html', 'cc', 2, ['a', 'b'])

    # Split Lectures 1 into 3 parts
    split_file('vedabase-app/vedabase-source/lec1.html', 'lec1', 3, ['a', 'b', 'c'])

    # Split Lectures 2 into 3 parts
    split_file('vedabase-app/vedabase-source/lec2.html', 'lec2', 3, ['a', 'b', 'c'])

    print("\n✓ All files split successfully!")

if __name__ == '__main__':
    main()
