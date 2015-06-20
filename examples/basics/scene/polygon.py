from vispy import app
import sys
from vispy.scene import SceneCanvas
from vispy.scene.visuals import Polygon, Ellipse, Rectangle
from vispy.color import Color

white = Color("#ecf0f1")
gray = Color("#121212")
red = Color("#e74c3c")
blue = Color("#2980b9")
orange = Color("#e88834")

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

    e = Ellipse(pos=(0.4, 0.2), radius=(0.1, 0.05),
                color=blue,
                border_width=2,
                border_color=white,
                parent=v.scene)

    r = Rectangle(pos=(0.6, 0.2), width=0.1, height=0.2,
                  color=orange,
                  border_width=2,
                  border_color=white,
                  radius=0.02,
                  parent=v.scene)

    e.num_segments = 50
    e.start_angle = 0
    e.span_angle = 135

    if sys.flags.interactive != 1:
        app.run()
