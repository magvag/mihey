from fontlab import CurrentFont, flGlyph
import re

'''
This script replaces diacritic names in auto-layer recipes with their case variants.
'''

font = CurrentFont()

replacements = {
    "dotaccent": "dotaccent.case",
    "dieresis": "dieresis.case",
    "acute": "acute.case",
    "hungarumlaut": "hungarumlaut.case",
    "ring": "ring.case",
    "macron": "macron.case",
    "caron": "caron.case",
    "circumflex": "circumflex.case",
    "tilde": "tilde.case",
    "breve": "breve.case",
    "commaaccent": "commaaccent.case",
    "uni0326": "commaaccent.case",
    "slash": "slash.case",
    "kratka": "kratka.case",
}

names = sorted(replacements, key=len, reverse=True)

pattern = re.compile(
    r"(?<![A-Za-z0-9_.])("
    + "|".join(re.escape(name) for name in names)
    + r")(?![A-Za-z0-9_.])"
)

for glyph in font.glyphs:
    g = flGlyph(glyph, font)

    for layer in g.layers:
        if not layer.autoLayer:
            continue

        recipe = layer.recipe
        if not recipe:
            continue

        new_recipe = pattern.sub(
            lambda m: replacements[m.group(1)],
            recipe
        )

        if new_recipe != recipe:
            print(f"**{g.name} [{layer.name}]:**")
            print(f"  {recipe}")
            print(f"→ {new_recipe}")

            layer.recipe = new_recipe

print("Done.")
