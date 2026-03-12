#!/usr/bin/env python3
"""
Update all HTML files to use local CSS/JS instead of external CDNs.
"""

import os
import glob

def update_html_file(filepath):
    """Update a single HTML file to use local resources."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Track if any changes were made
    original_content = content

    # Replace external CSS links with local ones
    content = content.replace(
        'https://fniessen.github.io/org-html-themes/src/readtheorg_theme/css/htmlize.css',
        'css/htmlize.css'
    )
    content = content.replace(
        'https://fniessen.github.io/org-html-themes/src/readtheorg_theme/css/readtheorg.css',
        'css/readtheorg.css'
    )

    # Replace external JS links with local ones
    content = content.replace(
        'https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js',
        'js/jquery.min.js'
    )
    content = content.replace(
        'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js',
        'js/bootstrap.min.js'
    )
    content = content.replace(
        'https://fniessen.github.io/org-html-themes/src/lib/js/jquery.stickytableheaders.min.js',
        'js/jquery.stickytableheaders.min.js'
    )
    content = content.replace(
        'https://fniessen.github.io/org-html-themes/src/readtheorg_theme/js/search.js',
        'js/search.js'
    )
    content = content.replace(
        'https://fniessen.github.io/org-html-themes/src/readtheorg_theme/js/readtheorg.js',
        'js/readtheorg.js'
    )

    # Only write if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    os.chdir('vedabase-app/vedabase-source')

    # Get all HTML files
    html_files = glob.glob('*.html')

    print(f"Found {len(html_files)} HTML files to update\n")

    updated_count = 0
    for html_file in sorted(html_files):
        if update_html_file(html_file):
            print(f"✓ Updated {html_file}")
            updated_count += 1
        else:
            print(f"  Skipped {html_file} (no changes needed)")

    print(f"\n✓ Updated {updated_count} files to use local resources")

if __name__ == '__main__':
    main()
