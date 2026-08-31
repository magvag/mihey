# -*- coding: utf-8 -*-

from typerig.proxy.fl.objects.font import eFont
from typerig.proxy.fl.objects.glyph import eGlyph
from typerig.proxy.fl.objects.shape import eShape

SC_SUFFIX = ".sc"
SC_PREFIX = "sc_"


def find_glyph(font, name):
    for g in font.pGlyphs():
        if g.name == name:
            return eGlyph(g.fl)
    return None


def source_transforms(glyph):
    """Return {element_name: transform} for all named shapes in glyph."""
    result = {}
    for shape in glyph.shapes():
        name = getattr(eShape(shape).data(), "name", None)
        if name:
            result[name] = shape.transform
    return result


def process_pair(font, source_name, destination_name):
    source = find_glyph(font, source_name)
    destination = find_glyph(font, destination_name)

    if source is None:
        print("Missing source:", source_name)
        return
    if destination is None:
        print("Missing destination:", destination_name)
        return

    print("\n%s -> %s" % (source_name, destination_name))

    transforms = source_transforms(source)

    for shape in destination.shapes():
        sc_name = getattr(eShape(shape).data(), "name", None)
        if not sc_name or not sc_name.startswith(SC_PREFIX):
            continue

        origin = sc_name[len(SC_PREFIX):]

        if origin not in transforms:
            print("  %s: no matching source shape '%s'" % (sc_name, origin))
            continue

        shape.transform = transforms[origin]
        print("  %s <- %s" % (sc_name, transforms[origin]))

    destination.update()


def selected_pairs(font):
    pairs = []
    for g in font.selected_pGlyphs():
        name = g.name
        if not name.endswith(SC_SUFFIX):
            print("Skipping (not a .sc glyph):", name)
            continue
        pairs.append((name[: -len(SC_SUFFIX)], name))
    return pairs


def main():
    font = eFont()
    pairs = selected_pairs(font)

    if not pairs:
        print("Nothing to do - select .sc glyph(s).")
        return

    for source_name, destination_name in pairs:
        process_pair(font, source_name, destination_name)

    font.update()
    print("\nDONE")


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception:
        traceback.print_exc()
