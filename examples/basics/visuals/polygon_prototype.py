from vispy import app
import sys
from vispy.scene import SceneCanvas
from vispy.scene.visuals import Polygon, Ellipse
from vispy.color import Color

white = Color("#ecf0f1")
gray = Color("#121212")
red = Color("#e74c3c")
blue = Color("#2980b9")

if __name__ == '__main__':
    canvas = SceneCanvas(keys='interactive', title='Polygon Example',
                         show=True)
    v = canvas.central_widget.add_view()
    v.bgcolor = gray
    v.camera = 'panzoom'

    cx, cy = (0.2, 0.2)
    halfx, halfy = (0.1, 0.1)

    rect_coords = [(cx - halfx, cy - halfy),
                   (cx + halfx, cy - halfy),
                   (cx + halfx, cy + halfy),
                   (cx - halfx, cy + halfy)]

    p = Polygon(rect_coords, color=red, border_color=white,
                border_width=3,  parent=v.scene)

    e = Ellipse(pos=(0.5, 0.2), radius=(0.1, 0.05),
                color=blue,
                parent=v.scene)

    if sys.flags.interactive != 1:
        app.run()
