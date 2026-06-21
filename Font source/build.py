#!/usr/bin/env python3
"""
Build script for Alcarin Tengwar font.
Fixes 3 pre-existing issues in the .glyphs source before building with fontmake.
"""

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import glyphsLib
from glyphsLib import GSFont


def fix_remove_sarinceliga_class(font):
    """Fix 1: Remove the disabled @sarinceliga class that references missing glyphs."""
    removed = 0
    font.classes = [c for c in font.classes if c.name != "sarinceliga" or (removed := removed + 1) == 0]
    # Simpler approach:
    to_remove = None
    for c in font.classes:
        if c.name == "sarinceliga":
            to_remove = c
            break
    if to_remove:
        font.classes.remove(to_remove)
        return True
    return False


def fix_remove_kern_feature(font):
    """Fix 2: Remove manual kern feature so glyphsLib auto-generates it correctly."""
    removed_kern = False
    modified_aalt = False

    # Remove kern feature
    to_remove = None
    for f in font.features:
        if f.name == "kern":
            to_remove = f
            break
    if to_remove:
        font.features.remove(to_remove)
        removed_kern = True

    # Remove "feature kern;" from aalt if present
    for f in font.features:
        if f.name == "aalt" and "feature kern;" in f.code:
            f.code = f.code.replace("feature kern;\n", "")
            f.code = f.code.replace("feature kern;", "")
            modified_aalt = True

    return removed_kern, modified_aalt


def fix_mark_categories(font):
    """Fix 3: Set category=Mark on glyphs with underscore-prefixed anchors."""
    fixed_count = 0
    already_set = 0

    for glyph in font.glyphs:
        has_mark_anchor = False
        for layer in glyph.layers:
            if layer.anchors:
                for anchor in layer.anchors:
                    if anchor.name.startswith("_"):
                        has_mark_anchor = True
                        break
            if has_mark_anchor:
                break

        if has_mark_anchor:
            if glyph.category == "Mark":
                already_set += 1
            else:
                glyph.category = "Mark"
                glyph.subCategory = "Nonspacing"
                fixed_count += 1

    return fixed_count, already_set


def get_ufo_glyphs(ufo_path):
    """Get set of glyph names in a UFO."""
    glyphs_dir = ufo_path / "glyphs"
    glyph_names = set()

    # Read from contents.plist or scan .glif files
    contents_plist = glyphs_dir / "contents.plist"
    if contents_plist.exists():
        import plistlib
        with open(contents_plist, "rb") as f:
            contents = plistlib.load(f)
            glyph_names = set(contents.keys())
    else:
        # Fallback: scan .glif files
        for glif in glyphs_dir.glob("*.glif"):
            # Extract glyph name from filename (simplified)
            glyph_names.add(glif.stem)

    return glyph_names


def postprocess_features_fea(ufo_path, glyph_names):
    """Comment out lines in features.fea that reference missing glyphs."""
    features_path = ufo_path / "features.fea"
    if not features_path.exists():
        return 0

    with open(features_path, "r") as f:
        content = f.read()

    lines = content.split("\n")
    modified_lines = []
    commented_count = 0
    in_class_def = False
    class_start_idx = None
    class_members_missing = True

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check for class definition start
        class_match = re.match(r'^@(\w+)\s*=\s*\[', stripped)
        if class_match and "];" not in stripped:
            # Multi-line class definition
            in_class_def = True
            class_start_idx = len(modified_lines)
            class_members_missing = True
            modified_lines.append(line)
            i += 1
            continue

        if in_class_def:
            modified_lines.append(line)
            # Check if any glyph in this line exists
            glyph_refs = re.findall(r'\b([A-Za-z_][A-Za-z0-9_.-]*)\b', stripped)
            for ref in glyph_refs:
                if ref in glyph_names:
                    class_members_missing = False

            if "];" in stripped:
                # End of class definition
                if class_members_missing and class_start_idx is not None:
                    # Comment out entire class definition
                    for j in range(class_start_idx, len(modified_lines)):
                        if not modified_lines[j].strip().startswith("#"):
                            modified_lines[j] = "# MISSING: " + modified_lines[j]
                            commented_count += 1
                in_class_def = False
                class_start_idx = None
            i += 1
            continue

        # Single-line class definition
        if class_match and "];" in stripped:
            glyph_refs = re.findall(r'\[([^\]]+)\]', stripped)
            if glyph_refs:
                members = re.findall(r'\b([A-Za-z_][A-Za-z0-9_.-]*)\b', glyph_refs[0])
                all_missing = all(m not in glyph_names for m in members if m)
                if all_missing and members:
                    modified_lines.append("# MISSING: " + line)
                    commented_count += 1
                    i += 1
                    continue

        # Check sub/pos lines for missing glyph references
        if stripped.startswith(("sub ", "pos ", "substitute ", "position ")):
            # Extract glyph names (simplified pattern)
            glyph_refs = re.findall(r'\b([A-Za-z_][A-Za-z0-9_.-]*)\b', stripped)
            # Filter out keywords
            keywords = {"sub", "pos", "substitute", "position", "by", "from", "lookup", "feature"}
            glyph_refs = [g for g in glyph_refs if g.lower() not in keywords and not g.startswith("@")]

            has_missing = any(g not in glyph_names for g in glyph_refs)
            if has_missing and glyph_refs:
                modified_lines.append("# MISSING: " + line)
                commented_count += 1
                i += 1
                continue

        modified_lines.append(line)
        i += 1

    if commented_count > 0:
        with open(features_path, "w") as f:
            f.write("\n".join(modified_lines))

    return commented_count


def main():
    print("=" * 60)
    print("Alcarin Tengwar Build Script")
    print("=" * 60)

    source_file = Path("Alcarin Tengwar.glyphs")
    if not source_file.exists():
        print(f"ERROR: Source file not found: {source_file}")
        return 1

    print(f"\nLoading {source_file}...")
    font = GSFont(str(source_file))
    print(f"  Loaded: {font.familyName}")
    print(f"  Glyphs: {len(font.glyphs)}")
    print(f"  Masters: {len(font.masters)}")

    # Apply fixes
    print("\n" + "-" * 40)
    print("Applying fixes...")
    print("-" * 40)

    # Fix 1
    if fix_remove_sarinceliga_class(font):
        print("  Fix 1: Removed disabled @sarinceliga class")
    else:
        print("  Fix 1: @sarinceliga class not found (already clean)")

    # Fix 2
    removed_kern, modified_aalt = fix_remove_kern_feature(font)
    if removed_kern:
        print("  Fix 2: Removed manual kern feature (will auto-generate)")
    if modified_aalt:
        print("         Also removed 'feature kern;' from aalt")

    # Fix 3
    fixed_marks, already_marks = fix_mark_categories(font)
    print(f"  Fix 3: Set Mark category on {fixed_marks} glyphs ({already_marks} already set)")

    # Convert to designspace
    print("\n" + "-" * 40)
    print("Converting to UFO/Designspace...")
    print("-" * 40)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Convert using glyphsLib
        designspace = glyphsLib.to_designspace(font)

        # Save UFOs
        for source in designspace.sources:
            ufo_path = tmpdir / Path(source.filename).name
            source.font.save(str(ufo_path))
            source.filename = str(ufo_path)
            print(f"  Saved: {ufo_path.name}")

        # Save designspace
        ds_path = tmpdir / "AlcarinTengwar.designspace"
        designspace.write(str(ds_path))
        print(f"  Saved: {ds_path.name}")

        # Decompose dot-inside ligature glyphs (component composites don't compile correctly)
        print("\n" + "-" * 40)
        print("Decomposing composite glyphs...")
        print("-" * 40)

        from fontTools.pens.t2CharStringPen import T2CharStringPen
        from fontTools.pens.recordingPen import DecomposingRecordingPen

        for source in designspace.sources:
            ufo = source.font
            decompose_glyphs = ['rightcurl_dotinside-teng', 'leftcurl_dotinside-teng']
            for glyph_name in decompose_glyphs:
                if glyph_name in ufo:
                    glyph = ufo[glyph_name]
                    if glyph.components:
                        # Use DecomposingRecordingPen to flatten components
                        rec_pen = DecomposingRecordingPen(ufo)
                        glyph.draw(rec_pen)

                        # Clear and redraw
                        glyph.clearContours()
                        glyph.clearComponents()
                        rec_pen.replay(glyph.getPen())
                        print(f"  Decomposed {glyph_name} in {Path(source.filename).name}")

            # Re-save the UFO
            ufo_path = Path(source.filename)
            ufo.save(str(ufo_path), overwrite=True)

        # Post-process features.fea in each UFO
        print("\n" + "-" * 40)
        print("Post-processing features.fea...")
        print("-" * 40)

        for source in designspace.sources:
            ufo_path = Path(source.filename)
            glyph_names = get_ufo_glyphs(ufo_path)
            commented = postprocess_features_fea(ufo_path, glyph_names)
            if commented > 0:
                print(f"  {ufo_path.name}: Commented out {commented} lines with missing glyphs")
            else:
                print(f"  {ufo_path.name}: No missing glyph references")

        # Build OTFs
        print("\n" + "-" * 40)
        print("Building OTF fonts...")
        print("-" * 40)

        output_dir = tmpdir / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                "fontmake",
                "-m", str(ds_path),
                "-o", "otf",
                "--output-dir", str(output_dir),
                "--keep-overlaps",
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("fontmake STDOUT:")
            print(result.stdout)
            print("fontmake STDERR:")
            print(result.stderr)
            print("ERROR: fontmake failed")
            return 1

        # Copy to build directory
        build_dir = Path("build")
        build_dir.mkdir(exist_ok=True)

        otf_files = list(output_dir.glob("*.otf"))
        if not otf_files:
            print("ERROR: No OTF files generated")
            return 1

        print("\n" + "-" * 40)
        print("Output files:")
        print("-" * 40)

        for otf in otf_files:
            dest = build_dir / otf.name
            shutil.copy(otf, dest)
            print(f"  {dest}")

    # Summary
    print("\n" + "=" * 60)
    print("BUILD COMPLETE")
    print("=" * 60)
    print(f"  Source: {source_file}")
    print(f"  Glyphs: {len(font.glyphs)}")
    print(f"  Marks fixed: {fixed_marks}")
    print(f"  Output: build/AlcarinTengwar-Regular.otf")
    print(f"          build/AlcarinTengwar-Bold.otf")

    return 0


if __name__ == "__main__":
    exit(main())
