# -*- coding: utf-8 -*-

from typerig.proxy.fl.objects.font import eFont
from typerig.proxy.fl.objects.glyph import eGlyph
from typerig.proxy.fl.objects.shape import eShape

SC_SUFFIX = ".sc"


def find_glyph(font, name):
    for g in font.pGlyphs():
        if g.name == name:
            return eGlyph(g.fl)
    return None


def describe_shapes(glyph):
    """
    Return the shape structure in order.

    Each item is:
        ("element", name)
        ("component", component_name)
        ("plain", None)
    """
    result = []

    for shape in glyph.shapes():
        data = eShape(shape).data()
        component = getattr(data, "componentGlyph", None)

        if component:
            result.append(("component", component))
        elif getattr(data, "name", None):
            result.append(("element", data.name))
        else:
            result.append(("plain", None))

    return result


def process_pair(font, source_name, destination_name, known_named_shapes):

    source = find_glyph(font, source_name)
    destination = find_glyph(font, destination_name)

    if source is None:
        print("Missing source:", source_name)
        return

    if destination is None:
        print("Missing destination:", destination_name)
        return


    shape = list(destination.shapes())[0]

    print("SHAPE TYPE:", type(shape))
    print("SHAPE ATTRS:")
    for x in dir(shape):
        if "ref" in x.lower() or "element" in x.lower() or "link" in x.lower() or "copy" in x.lower():
            print(x, getattr(shape, x, None))
    source_info = describe_shapes(source)
    destination_shapes = list(destination.shapes())
    destination_layer_name = destination.activeLayer().name

    print("\n%s -> %s" % (source_name, destination_name))

    print("SOURCE:")
    for i, item in enumerate(source_info):
        print("  %d: %s" % (i, item))

    print("DESTINATION:")
    for i, shape in enumerate(destination_shapes):
        data = eShape(shape).data()
        print(
            "  %d: component=%r name=%r"
            % (i, getattr(data, "componentGlyph", None), getattr(data, "name", None))
        )

    # ------------------------------------------------------------
    # Safety check
    # ------------------------------------------------------------

    if len(source_info) != len(destination_shapes):
        raise RuntimeError(
            "%s -> %s: shape count differs: source=%d destination=%d"
            % (source_name, destination_name, len(source_info), len(destination_shapes))
        )

    # ------------------------------------------------------------
    # Apply names / component references
    # ------------------------------------------------------------

    for i, ((kind, value), raw_shape) in enumerate(zip(source_info, destination_shapes)):

        eshape = eShape(raw_shape)
        data = eshape.data()

        # --------------------------------------------------------
        # Named element
        # --------------------------------------------------------

        if kind == "element":

            if getattr(data, "componentGlyph", None):
                raise RuntimeError(
                    "%s -> %s: expected element at shape #%d, "
                    "but destination is a component."
                    % (source_name, destination_name, i)
                )

            new_name = "sc_" + value

            # Check our own registry first (shapes named earlier in this
            # run), then fall back to the font's index for elements that
            # already existed before the script started.
            existing = known_named_shapes.get(new_name)
            if existing is None:
                existing = font.findShape(new_name, master=destination_layer_name)

            if existing is not None and existing is not raw_shape:

                old_transform = raw_shape.transform

                destination.replaceShape(raw_shape, existing, destination_layer_name)

                # replaceShape invalidates raw_shape; re-fetch by index
                fresh = list(destination.shapes())[i]
                fresh.transform = old_transform


                # replaceShape invalidates raw_shape; re-fetch by index
                fresh = list(destination.shapes())[i]
                fresh.transform = old_transform


                known_named_shapes[new_name] = fresh

                print(
                    "  element #%d: %s -> LINKED to existing '%s'"
                    % (i, value, new_name)
                )
            else:
                data.name = new_name
                known_named_shapes[new_name] = raw_shape

                print(
                    "  element #%d: %s -> %s (renamed, first occurrence)"
                    % (i, value, new_name)
                )

        # --------------------------------------------------------
        # Component
        # --------------------------------------------------------

        elif kind == "component":

            actual_component = getattr(data, "componentGlyph", None)

            if not actual_component:
                raise RuntimeError(
                    "%s -> %s: expected component at shape #%d."
                    % (source_name, destination_name, i)
                )

            # Component convention:
            #
            #     L -> L.sc
            #
            # NOT:
            #
            #     L -> sc_L
            #
            new_name = actual_component + ".sc"
            data.componentGlyph = new_name

            print(
                "  component #%d: %s -> %s"
                % (i, actual_component, new_name)
            )

        # --------------------------------------------------------
        # Unnamed / plain shape
        # --------------------------------------------------------

        elif kind == "plain":
            pass

    destination.update()


def selected_pairs(font):
    """
    Build (source_name, destination_name) pairs from the current
    selection. Only glyphs whose name ends with '.sc' are treated
    as destinations; the source name is derived by stripping the
    suffix. Anything else in the selection is skipped.
    """
    pairs = []

    for g in font.selected_pGlyphs():
        name = g.name

        if not name.endswith(SC_SUFFIX):
            print("Skipping (not a .sc glyph):", name)
            continue

        source_name = name[: -len(SC_SUFFIX)]
        pairs.append((source_name, name))

    return pairs


def main():

    font = eFont()
    known_named_shapes = {}

    pairs = selected_pairs(font)

    if not pairs:
        print("Nothing to do - select the '.sc' destination glyph(s).")
        return

    for source_name, destination_name in pairs:
        process_pair(font, source_name, destination_name, known_named_shapes)

    font.update()
    print("\nDONE")


if __name__ == "__main__":

    import traceback

    try:
        main()
    except Exception:
        traceback.print_exc()
