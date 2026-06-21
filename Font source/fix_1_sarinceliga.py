#!/usr/bin/env python3
"""
Fix 1: Remove @sarinceliga class that references nonexistent glyphs.

The class has disabled=1 and references 57 glyph names that don't exist.
GlyphsApp skips it; glyphsLib doesn't, causing build failures.
"""

import re
import sys

FONT_PATH = "Alcarin Tengwar.glyphs"


def main():
    print(f"Loading {FONT_PATH}...")
    with open(FONT_PATH, 'r') as f:
        content = f.read()

    # Find and remove the sarinceliga class block
    # Pattern: { ... name = sarinceliga; ... },
    # The class block starts with { and ends with },

    # Find "name = sarinceliga;"
    marker = 'name = sarinceliga;'
    idx = content.find(marker)

    if idx < 0:
        print("sarinceliga class not found - already fixed?")
        return 0

    # Find the start of this class block (opening brace)
    # Search backwards for the opening {
    start = content.rfind('{', 0, idx)
    if start < 0:
        print("ERROR: could not find class block start")
        return 1

    # Find the end of this class block (closing },)
    end = content.find('},', idx)
    if end < 0:
        print("ERROR: could not find class block end")
        return 1
    end += 2  # include the "},\n"

    # Check if there's a newline after
    if end < len(content) and content[end] == '\n':
        end += 1

    # Extract the block to show what we're removing
    block = content[start:end]
    print(f"\nRemoving class block ({len(block)} chars):")
    print(f"  starts with: {block[:60]}...")
    print(f"  ends with: ...{block[-40:]}")

    # Remove the block
    content = content[:start] + content[end:]

    # Save
    print(f"\nSaving to {FONT_PATH}...")
    with open(FONT_PATH, 'w') as f:
        f.write(content)

    # Verify
    if 'sarinceliga' in content:
        print("WARNING: sarinceliga still found in file")
        return 1

    print("Done. sarinceliga class removed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
