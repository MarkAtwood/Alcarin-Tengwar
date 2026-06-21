#!/usr/bin/env python3
"""
Fix 2: Remove manual kern feature that references auto-generated class names.

The kern feature uses @MMK_L_xxx / @MMK_R_xxx names that GlyphsApp generates
at export. glyphsLib maps these differently, causing undefined class errors.

Solution: Remove the manual kern feature. The kerning data is in the source
metadata; GlyphsApp/glyphsLib will auto-generate the feature correctly.
"""

import re
import sys

FONT_PATH = "Alcarin Tengwar.glyphs"


def main():
    print(f"Loading {FONT_PATH}...")
    with open(FONT_PATH, 'r') as f:
        content = f.read()

    # Find the kern feature in the features array
    # Pattern in .glyphs plist:
    # {
    # automatic = 1;
    # code = "...";
    # name = kern;
    # },

    marker = 'name = kern;'
    idx = content.find(marker)

    if idx < 0:
        print("kern feature not found - already fixed?")
        return 0

    # Find the start of this feature block
    start = content.rfind('{', 0, idx)
    if start < 0:
        print("ERROR: could not find feature block start")
        return 1

    # Find the end (closing },)
    end = content.find('},', idx)
    if end < 0:
        # Might be the last feature, try just }
        end = content.find('}', idx)
        if end < 0:
            print("ERROR: could not find feature block end")
            return 1
        end += 1
    else:
        end += 2

    # Include trailing newline
    if end < len(content) and content[end] == '\n':
        end += 1

    block = content[start:end]

    # Verify this is the kern feature
    if 'name = kern;' not in block:
        print("ERROR: block doesn't contain kern feature")
        return 1

    print(f"\nRemoving kern feature block ({len(block)} chars):")
    print(f"  starts with: {block[:80]}...")

    # Remove
    content = content[:start] + content[end:]

    # Also remove "feature kern;\n" from aalt if present
    aalt_kern = 'feature kern;\\012'
    if aalt_kern in content:
        content = content.replace(aalt_kern, '')
        print("  Also removed 'feature kern;' from aalt")

    # Save
    print(f"\nSaving to {FONT_PATH}...")
    with open(FONT_PATH, 'w') as f:
        f.write(content)

    # Verify
    if 'name = kern;' in content:
        print("WARNING: kern feature still found")
        return 1

    print("Done. kern feature removed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
