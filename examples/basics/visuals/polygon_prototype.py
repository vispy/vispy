from vispy import app
import sys
from vispy.scene import SceneCanvas
from vispy.scene.visuals import Polygon

if __name__ == '__main__':
    canvas = SceneCanvas(keys='interactive', title='Polygon Example',
                         show=True)
    v = canvas.central_widget.add_view()
    v.bgcolor = (0.3, 0.3, 0.3, 1)
    v.camera = 'panzoom'

    cx, cy = (0.5, 0.5)
    halfx, halfy = (0.3, 0.3)

    rect_coords = [(cx - halfx, cy - halfy),
                   (cx + halfx, cy - halfy),
                   (cx + halfx, cy + halfy),
                   (cx - halfx, cy + halfy)]

    p = Polygon(rect_coords, color="red", border_color="white",
                border_width=10,  parent=v.scene)

    if sys.flags.interactive != 1:
        app.run()
