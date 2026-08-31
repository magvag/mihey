import fontlab as fl
from PythonQt.QtCore import QPointF
from typerig.proxy.fl.objects.font import eFont
from typerig.proxy.fl.objects.glyph import eGlyph
from typerig.proxy.fl.objects.shape import eShape


def process_glyph(glyph):
    new_shape = fl.flShape()

    for shape in glyph.shapes():
        shape_transform = shape.transform
        for contour in shape.contours:
            cloned = contour.clone()
            for node in cloned.nodes():
                p = shape_transform.map(QPointF(node.x, node.y))
                node.x, node.y = p.x(), p.y()
            new_shape.shapeData.addContours([cloned])

    added_shape = glyph.addShape(new_shape)
    added_shape.contentLocked = True
    added_shape = eShape(added_shape)
    added_shape.setName(glyph.name)

    added_shape.scale(0.818, 0.685)

    for contour in added_shape.contours():
        contour.closed = False

    added_shape.update()
    glyph.update()
    print("Processed:", glyph.name)


def main():
    font = eFont()
    selected = list(font.selected_pGlyphs())

    if not selected:
        print("No glyphs selected.")
        return

    for g in selected:
        process_glyph(eGlyph(g.fl))

    font.update()
    print("\nDONE")


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception:
        traceback.print_exc()
