from ..node import Node


class Anchor(Node):
    """
    Anchor is a node derives parts of its transform from some other
    coordinate system in the scene.

    The purpose is to allow children of an Anchor to draw using a position
    (and optionally rotation) specified by one coordinate system, and scaling/
    projection specified by another.

    For example, text attached to a point in a 3D scene should be drawn in
    a coordinate system with a simple relationship to the screen pixels, but
    should derive its location from a position within the 3D coordinate
    system::

        root = Box()
        view = ViewBox(parent=box)
        plot = LineVisual(parent=ViewBox)
        anchor = Anchor(parent=root, anchor_to=plot, anchor_pos=(10, 0))
        text = Text(parent=anchor,
                    text="Always points to (10,0) relative to line.")

    """
