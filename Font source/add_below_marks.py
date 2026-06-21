#!/usr/bin/env python3
"""
Add Extended mode glyphs to Alcarin Tengwar by direct text manipulation
of the .glyphs plist format, avoiding glyphsLib serialization bugs.
"""

import re

FONT_PATH = "Alcarin Tengwar.glyphs"
OUTPUT_PATH = "Alcarin Tengwar.glyphs"  # in-place modification

REGULAR_ID = "4397B867-53E7-4964-BB9B-A578920F109C"
BOLD_ID = "0ED38B93-C2B0-4B4A-9C6D-D7838A33C317"


def make_below_mark(name, unicode_hex, source_name, 
                    reg_width, bold_width,
                    reg_offset, bold_offset,
                    reg_bottom_x, reg_bottom_y, reg_bottom2_x, reg_bottom2_y,
                    bold_bottom_x, bold_bottom_y, bold_bottom2_x, bold_bottom2_y):
    """Generate a .glyphs plist block for a below-combining mark."""
    return f"""{{
glyphname = "{name}";
lastChange = "2026-02-11 23:00:00 +0000";
layers = (
{{
anchors = (
{{
name = _bottom;
position = "{{{reg_bottom_x}, 0}}";
}},
{{
name = bottom;
position = "{{{reg_bottom2_x}, {reg_bottom2_y}}}";
}}
);
components = (
{{
name = "{source_name}";
transform = "{{1, 0, 0, 1, 0, {reg_offset}}}";
}}
);
layerId = "{REGULAR_ID}";
width = {reg_width};
}},
{{
anchors = (
{{
name = _bottom;
position = "{{{bold_bottom_x}, 0}}";
}},
{{
name = bottom;
position = "{{{bold_bottom2_x}, {bold_bottom2_y}}}";
}}
);
components = (
{{
name = "{source_name}";
transform = "{{1, 0, 0, 1, 0, {bold_offset}}}";
}}
);
layerId = "{BOLD_ID}";
width = {bold_width};
}}
);
leftMetricsKey = "=20";
rightMetricsKey = "=20";
unicode = {unicode_hex};
}},
"""


def make_dotinside_ligature(name, unicode_hex, base_name,
                            reg_width, bold_width,
                            reg_top_x, reg_top_y, reg_top2_x, reg_top2_y,
                            bold_top_x, bold_top_y, bold_top2_x, bold_top2_y,
                            reg_dot_x_off, reg_dot_y_off, bold_dot_x_off, bold_dot_y_off):
    """Generate a .glyphs plist block for a tehta+dotinside ligature."""
    return f"""{{
glyphname = "{name}";
lastChange = "2026-02-11 23:00:00 +0000";
layers = (
{{
anchors = (
{{
name = _top;
position = "{{{reg_top_x}, {reg_top_y}}}";
}},
{{
name = top;
position = "{{{reg_top2_x}, {reg_top2_y}}}";
}}
);
components = (
{{
name = "{base_name}";
}},
{{
name = "dotinside-teng";
transform = "{{1, 0, 0, 1, {reg_dot_x_off}, {reg_dot_y_off}}}";
}}
);
layerId = "{REGULAR_ID}";
width = {reg_width};
}},
{{
anchors = (
{{
name = _top;
position = "{{{bold_top_x}, {bold_top_y}}}";
}},
{{
name = top;
position = "{{{bold_top2_x}, {bold_top2_y}}}";
}}
);
components = (
{{
name = "{base_name}";
}},
{{
name = "dotinside-teng";
transform = "{{1, 0, 0, 1, {bold_dot_x_off}, {bold_dot_y_off}}}";
}}
);
layerId = "{BOLD_ID}";
width = {bold_width};
}}
);
leftMetricsKey = "=20";
rightMetricsKey = "=20";
unicode = {unicode_hex};
}},
"""


def main():
    print(f"Loading {FONT_PATH}...")
    with open(FONT_PATH, 'r') as f:
        content = f.read()

    # Build all new glyph blocks
    new_glyphs = []

    # Below marks: (name, unicode, source, reg_w, bold_w, reg_off, bold_off,
    #               reg_bx, reg_by, reg_b2x, reg_b2y, bold_bx, bold_by, bold_b2x, bold_b2y)
    below_marks = [
        # gravebelow: from grave-teng (w=267/267, _top at 153/153, top at 134/134, top_y 623/643)
        ("gravebelow-teng", "E097", "grave-teng",
         267, 267, -730, -750,
         153, 0, 134, -127,   # reg: _bottom, bottom
         153, 0, 134, -127),  # bold: _bottom, bottom

        # caronbelow: from caron-teng (w=294/306, _top at 147/147, top at 147/147, top_y 600/630)
        ("caronbelow-teng", "E096", "caron-teng",
         294, 306, -730, -750,
         147, 0, 147, -150,
         147, 0, 147, -140),

        # brevebelow: from breve-teng (w=331/345, _top at 166/166, top at 166/166, top_y 590/630)
        ("brevebelow-teng", "E099", "breve-teng",
         331, 345, -730, -750,
         166, 0, 166, -160,
         166, 0, 166, -140),

        # tildebelow: from tilde-teng (w=380/390, _top at 210/210, top at 230/230, top_y 553/593)
        ("tildebelow-teng", "E09A", "tilde-teng",
         380, 390, -650, -685,
         210, 0, 230, -117,
         210, 0, 230, -112),

        # wavebelow: from wave-teng (w=488/488, _top at 244/244, top at 244/244, top_y 555/599)
        ("wavebelow-teng", "E09B", "wave-teng",
         488, 488, -650, -685,
         244, 0, 244, -115,
         244, 0, 244, -106),

        # ringbelow: from ring-teng (w=231/251, _top at 116/126, top at 116/126, top_y 643/663)
        ("ringbelow-teng", "E09C", "ring-teng",
         231, 251, -730, -750,
         116, 0, 116, -107,
         126, 0, 126, -107),

        # dottripleturnedbelow: from dottripleturnedabove-teng (w=318/334, _top 159/167, top 159/167, top_y 628/668)
        ("dottripleturnedbelow-teng", "E09D", "dottripleturnedabove-teng",
         318, 334, -730, -750,
         159, 0, 159, -122,
         167, 0, 167, -102),
    ]

    for args in below_marks:
        block = make_below_mark(*args)
        new_glyphs.append(block)
        print(f"  + {args[0]} (U+{args[1]})")

    # Dot-inside ligatures
    # rightcurl-teng: w=219/239, _top at (107,400)/(119,420), top at (130,578)/(142,608)
    # leftcurl-teng: w=219/239, _top at (112,400)/(119,420), top at (89,578)/(77,608)
    # Transforms from BUILD_GUIDE:
    # - rightcurl_dotinside-teng: {1, 0, 0, 1, 140, 380} (Regular), {1, 0, 0, 1, 150, 390} (Bold)
    # - leftcurl_dotinside-teng: {1, 0, 0, 1, 125, 370} (Regular), {1, 0, 0, 1, 135, 380} (Bold)
    dot_inside = [
        ("rightcurl_dotinside-teng", "E098", "rightcurl-teng",
         219, 239,
         107, 400, 130, 578,   # reg anchors
         119, 420, 142, 608,   # bold anchors
         140, 380, 150, 390),  # reg x/y, bold x/y

        ("leftcurl_dotinside-teng", "E09E", "leftcurl-teng",
         219, 239,
         112, 400, 89, 578,
         119, 420, 77, 608,
         125, 370, 135, 380),
    ]

    for args in dot_inside:
        block = make_dotinside_ligature(*args)
        new_glyphs.append(block)
        print(f"  + {args[0]} (U+{args[1]})")

    # Insert new glyphs before the closing of the glyphs array
    # The glyphs array ends with ");\n" before other top-level keys
    # Find the last glyph block and insert after it
    # The glyphs array is: glyphs = ( ... );
    # We need to find the end of the last glyph entry

    # Strategy: find the last occurrence of a glyph block end pattern
    # Each glyph ends with "},\n" before either the next "{" or ");"
    
    # Find the glyphs array
    glyphs_start = content.find("glyphs = (")
    if glyphs_start < 0:
        print("ERROR: could not find glyphs array")
        return

    # Find the closing ");" of the glyphs array
    # We need to match the right one - it's after all the glyph blocks
    # Search from end for the pattern "}\n);" which closes the glyphs array
    # Actually, let's find it by counting brace depth from glyphs_start
    
    # Simpler: find ");\ninstances" or ");\nfontMaster" or similar top-level key after glyphs
    # In Glyphs format, after glyphs comes other top-level keys
    
    # Find pattern: the glyphs array closing is "};\n);\n" followed by a top-level key
    # Let's search for the pattern where a glyph closes and the array closes
    
    # Look for the last "unicode = E109;\n},\n" (last glyph in original) and insert after
    last_glyph_pattern = "unicode = E109;\n},\n"
    last_pos = content.rfind(last_glyph_pattern)
    if last_pos < 0:
        # Try alternate: find last glyph closing before ");" 
        print("WARNING: could not find last glyph marker, searching for array end")
        # Find ");\n" after glyphs that's followed by a top-level key
        search_pos = glyphs_start
        array_end = -1
        while True:
            pos = content.find(");\n", search_pos)
            if pos < 0:
                break
            # Check if this is the glyphs array end
            next_content = content[pos+3:pos+50].strip()
            if next_content.startswith(("instances", "fontMaster", "unitsPerEm")):
                array_end = pos
                break
            search_pos = pos + 1
        if array_end < 0:
            print("ERROR: could not find glyphs array end")
            return
        insert_pos = array_end
    else:
        insert_pos = last_pos + len(last_glyph_pattern)

    # Insert new glyphs
    new_glyph_text = "\n".join(new_glyphs)
    content = content[:insert_pos] + new_glyph_text + content[insert_pos:]
    print(f"\n  Inserted {len(new_glyphs)} glyph blocks")

    # Update @accBottom class
    acc_bottom_pattern = r'(name = accBottom;\n}'
    # Find the accBottom class code and append new names
    new_below_names = "\n".join([m[0] for m in below_marks])
    
    # Find accBottom class block
    ab_idx = content.find('name = accBottom;')
    if ab_idx >= 0:
        # Find the code = "..." before it
        code_end = content.rfind('";', 0, ab_idx)
        if code_end >= 0:
            # Insert before the closing quote
            insert_str = "\\012" + "\\012".join([m[0] for m in below_marks]) + "\\012"
            content = content[:code_end] + insert_str + content[code_end:]
            print("  Updated @accBottom class")
    
    # Update @accAll class (same approach)
    aa_idx = content.find('name = accAll;')
    if aa_idx >= 0:
        code_end = content.rfind('";', 0, aa_idx)
        if code_end >= 0:
            insert_str = "\\012" + "\\012".join([m[0] for m in below_marks]) + "\\012"
            content = content[:code_end] + insert_str + content[code_end:]
            print("  Updated @accAll class")

    # Update ccmp feature: add dotinside ligature rules
    dotinside_marker = "} dotinsideLigature;"
    di_idx = content.find(dotinside_marker)
    if di_idx >= 0:
        new_rules = (
            "\\tsub rightcurl-teng dotinside-teng by rightcurl_dotinside-teng;\\012"
            "\\tsub leftcurl-teng dotinside-teng by leftcurl_dotinside-teng;\\012"
        )
        content = content[:di_idx] + new_rules + content[di_idx:]
        print("  Updated ccmp dotinsideLigature lookup")

    # Save
    print(f"\nSaving to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w') as f:
        f.write(content)

    # Verify by re-reading
    print("\nVerifying...")
    for m in below_marks:
        if f'glyphname = "{m[0]}"' in content:
            print(f"  ✓ {m[0]}")
        else:
            print(f"  ✗ {m[0]} MISSING")
    for d in dot_inside:
        if f'glyphname = "{d[0]}"' in content:
            print(f"  ✓ {d[0]}")
        else:
            print(f"  ✗ {d[0]} MISSING")

    print("\nDone.")


if __name__ == "__main__":
    main()
