import sys
import numpy as np
from vispy.scene import visuals
from vispy import scene

canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='k')

view = canvas.central_widget.add_view()
view.camera = 'arcball'
view.camera.fov = 70
enc = visuals.Sphere(radius=1, color=(0, 0, 1), rows=300, cols=300, depth=300,
                             edge_color=None, shading='textured_globe', parent=view.scene)

axis = visuals.XYZAxis(parent=view.scene, width=1)


if __name__ == '__main__':
    canvas.app.run()
