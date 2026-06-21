# Alcarin Tengwar: Build Guide

## Overview

This fork adds 9 glyphs to Toshi Omagari's Alcarin Tengwar font
(OFL-licensed, https://github.com/Tosche/Alcarin-Tengwar) to complete the
below-mark diacritic inventory and add dot-inside tehta variants.

These additions fill gaps implied by Tengwar's systematic structure:
- If an above-mark exists, its below counterpart should exist
- If dot-inside modification works for some tehtar, it should work for curls

The extended font supports tonal Tengwar modes (Mandarin, Cantonese, Vietnamese, etc.)
and any mode needing below-tengwa diacritics or modified vowel tehtar.

## New Glyphs

| Codepoint | Glyph Name | Purpose |
|-----------|-----------|---------|
| U+E096 | caronbelow-teng | Below caron (ˇ) — completes above/below symmetry |
| U+E097 | gravebelow-teng | Below grave (`) — completes above/below symmetry |
| U+E098 | rightcurl_dotinside-teng | Right curl with interior dot — modified vowel |
| U+E099 | brevebelow-teng | Below breve — completes above/below symmetry |
| U+E09A | tildebelow-teng | Below tilde — completes above/below symmetry |
| U+E09B | wavebelow-teng | Below wave — completes above/below symmetry |
| U+E09C | ringbelow-teng | Below ring — completes above/below symmetry |
| U+E09D | dottripleturnedbelow-teng | Below triple-dot-turned — completes symmetry |
| U+E09E | leftcurl_dotinside-teng | Left curl with interior dot — modified vowel |

Pre-existing below marks (already in upstream):
- U+E051 macronbelow-teng
- U+E047 acutebelow-teng
- U+E043 dotdblbelow-teng

## Two-Stage Pipeline

### Stage 1: Patch the source (`add_below_marks.py`)

Operates on the original `Alcarin Tengwar.glyphs` from upstream.
Produces `Alcarin Tengwar.glyphs` with:
- 7 new below-combining marks (component refs to above marks with Y offset)
- 2 new dot-inside tehta ligatures (component composites)
- Updated @accBottom and @accAll glyph classes
- Updated ccmp feature with dot-inside ligature substitution rules

Below marks use these transforms (matching existing acutebelow/macronbelow):
- Tall marks (grave, caron, breve, ring, dottripleturned): Y offset -730 (Regular), -750 (Bold)
- Short marks (tilde, wave): Y offset -650 (Regular), -685 (Bold)

Dot-inside ligatures use these component transforms:
- rightcurl_dotinside-teng: {1, 0, 0, 1, 140, 380} (Regular), {1, 0, 0, 1, 150, 390} (Bold)
- leftcurl_dotinside-teng: {1, 0, 0, 1, 125, 370} (Regular), {1, 0, 0, 1, 135, 380} (Bold)

### Stage 2: Build OTFs (`build.py`)

Loads `Alcarin Tengwar.glyphs`, applies 3 fixes, builds OTFs.

## Build Fixes (Pre-Existing Issues in Upstream)

### Fix 1: Remove disabled @sarinceliga class

The source has a class `@sarinceliga` with `disabled=1` referencing 57 glyph
names that don't exist. GlyphsApp skips disabled classes at export; glyphsLib
doesn't, causing build failure.

**Action:** `font.classes = [c for c in font.classes if c.name != 'sarinceliga']`

### Fix 2: Remove manual kern feature

The kern feature references `@MMK_L_xxx` / `@MMK_R_xxx` class names that
GlyphsApp auto-generates. glyphsLib maps these to `@public.kern1/2` naming
but doesn't rewrite the feature code, so class names become undefined.

**Action:** Remove the kern feature from `font.features`. Also strip
`feature kern;\n` from aalt if present. glyphsLib auto-generates correct
kern code from kerning metadata during UFO conversion.

### Fix 3: Set mark categories on combining glyphs

GlyphsApp infers `category=Mark` from `_top`/`_bottom` anchor names.
glyphsLib doesn't. Without explicit categories, GDEF mark classes won't be
generated, and mark/mkmk features won't be auto-built.

**Action:** For every glyph with any anchor starting with `_`, set
`glyph.category = "Mark"` and `glyph.subCategory = "Nonspacing"`.

### Safety net: Comment out missing glyph references

After UFO conversion, scan each UFO's `features.fea` for glyph names that
don't exist in that UFO's `glyphs/` directory. Comment out lines containing
such names.

## File Layout

```
Font source/
  Alcarin Tengwar.glyphs   # source (modified from upstream)
  add_below_marks.py       # script that adds the 9 glyphs
  build.py                 # build OTFs with fontmake
  build/
    AlcarinTengwar-Regular.otf
    AlcarinTengwar-Bold.otf
```

## Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install glyphsLib fontmake ufoLib2 fonttools
```

## Verification

```python
from fontTools.ttLib import TTFont

font = TTFont('build/AlcarinTengwar-Regular.otf')
cmap = font.getBestCmap()

# New glyphs present
for cp in [0xE096, 0xE097, 0xE098, 0xE099, 0xE09A, 0xE09B, 0xE09C, 0xE09D, 0xE09E]:
    assert cp in cmap, f"U+{cp:04X} missing from cmap"
print(f"All 9 new codepoints present")

# GDEF mark class populated
gdef = font['GDEF'].table
marks = [g for g, c in gdef.GlyphClassDef.classDefs.items() if c == 3]
assert len(marks) > 80, f"Only {len(marks)} marks in GDEF"
print(f"GDEF contains {len(marks)} mark glyphs")

# mark feature exists in GPOS
gpos_features = [r.FeatureTag for r in font['GPOS'].table.FeatureList.FeatureRecord]
assert 'mark' in gpos_features, "mark feature missing"
print(f"GPOS features: {sorted(set(gpos_features))}")

print("All checks passed")
font.close()
```
