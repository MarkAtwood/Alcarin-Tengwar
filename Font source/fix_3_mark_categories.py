#!/usr/bin/env python3
"""
Fix 3: Add explicit category=Mark to all combining mark glyphs.

GlyphsApp infers Mark category from _top/_bottom anchor names.
glyphsLib doesn't, so GDEF mark class is incomplete.

Solution: Add explicit category and subCategory to all glyphs with _ anchors.
"""

import re
import sys

FONT_PATH = "Alcarin Tengwar.glyphs"


def main():
    print(f"Loading {FONT_PATH}...")
    with open(FONT_PATH, 'r') as f:
        content = f.read()

    # Find all glyphs that have anchors starting with _
    # These are combining marks that need category = Mark

    # Strategy: Find each glyph block, check if it has _top or _bottom anchor,
    # and if so, add category/subCategory if not present

    # Glyph blocks are in the glyphs = ( ... ); array
    # Each glyph: { glyphname = "..."; ... },

    # We'll use regex to find glyphs with _ anchors
    # Pattern for anchor: name = _something;

    fixed_count = 0
    already_set = 0

    # Find all glyph blocks
    # Pattern: starts with { after glyphs = ( and ends with },

    glyphs_start = content.find('glyphs = (')
    if glyphs_start < 0:
        print("ERROR: could not find glyphs array")
        return 1

    # Process each glyph block
    # We need to be careful with nested braces

    pos = glyphs_start + len('glyphs = (')
    modified_content = content[:pos]

    while True:
        # Skip whitespace
        while pos < len(content) and content[pos] in ' \t\n':
            modified_content += content[pos]
            pos += 1

        if pos >= len(content):
            break

        # Check for end of glyphs array
        if content[pos:pos+2] == ');':
            modified_content += content[pos:]
            break

        # Expect a glyph block starting with {
        if content[pos] != '{':
            # Not a glyph block, just copy
            modified_content += content[pos]
            pos += 1
            continue

        # Find the matching closing }
        brace_depth = 0
        block_start = pos
        while pos < len(content):
            if content[pos] == '{':
                brace_depth += 1
            elif content[pos] == '}':
                brace_depth -= 1
                if brace_depth == 0:
                    pos += 1
                    break
            pos += 1

        # Include trailing comma if present
        if pos < len(content) and content[pos] == ',':
            pos += 1

        block = content[block_start:pos]

        # Check if this glyph has _ anchors
        has_underscore_anchor = bool(re.search(r'name = _\w+;', block))

        if has_underscore_anchor:
            # Check if category is already set
            has_category = 'category = ' in block

            if has_category:
                already_set += 1
                modified_content += block
            else:
                # Add category after glyphname line
                # Find "glyphname = ...;" and insert after
                match = re.search(r'(glyphname = "[^"]+";)', block)
                if match:
                    insert_pos = match.end()
                    new_block = (
                        block[:insert_pos] +
                        '\ncategory = Mark;\nsubCategory = Nonspacing;' +
                        block[insert_pos:]
                    )
                    modified_content += new_block
                    fixed_count += 1
                else:
                    # Couldn't find glyphname, just copy
                    modified_content += block
        else:
            modified_content += block

    print(f"\nFixed {fixed_count} glyphs (added category = Mark)")
    print(f"Already had category: {already_set}")

    if fixed_count == 0:
        print("No changes needed.")
        return 0

    # Save
    print(f"\nSaving to {FONT_PATH}...")
    with open(FONT_PATH, 'w') as f:
        f.write(modified_content)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
