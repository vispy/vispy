"""
Simple test of stacking viewboxes, demonstrating the three methods that
can be used by a viewbox to provide clipping.

There is one root scene with an NDC camera. It contains two viewboxes.
One with an NDC camera on the left, and one with a pixel camera on the
right. Each of these viewboxes contains again two viewboxes. One with
ndc camera at the bottom, and one with a pixel camera at the top.

Use the global PREFER_PIXEL_GRID variables to set the clipping method
for the two toplevel and four leaf viewbox, respectively. You can also
manyally set the preferred_clip_method property of one or more viewboxes.

"""

import numpy as np

from vispy import app, gloo
from vispy import scene

#gloo.gl.use('desktop debug')

# <<< Change method here
# With the none method you can see the absence of clipping.
# With the fbo method you can see the texture interpolation (induced by
# a delibirate mismatch in screen and textue resolution)
# Try different combinarions, like a viewport in an fbo
PREFER_PIXEL_GRID1 = 'viewport'  # none, viewport, fbo (fragment to come)
PREFER_PIXEL_GRID2 = 'viewport'


# Create lines for use in ndc and pixel coordinates
N = 1000
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]
pos = np.empty((N, 2), np.float32)
#
pos[:, 0] = np.linspace(-1., 1., N)
pos[:, 1] = np.random.normal(0.0, 0.5, size=N)
pos[:20, 1] = -0.5  # So we can see which side is down
line_ndc = scene.visuals.Line(pos=pos.copy(), color=color)
#
pos[:, 0] = np.linspace(50, 350., N)
pos[:, 1] = 150 + pos[:, 1] * 50
pos[:20, 1] = 100  # So we can see which side is down
line_pixels = scene.visuals.Line(pos=pos.copy(), color=color)

# Create canvas
canvas = scene.SceneCanvas(size=(800, 600), show=True, close_keys='escape')
canvas.scene.camera = scene.cameras.Camera()  # null

vb1 = scene.ViewBox(canvas.scene)
vb1.preferred_clip_method = 'viewport'
vb1.pos = 100, 100
vb1.size = 200, 200
vb1.scene.camera = scene.cameras.TwoDCamera()

line_ndc.add_parent(vb1.scene)

box = np.array([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]], dtype=np.float32)
unit_box = scene.visuals.Line(pos=box, color=(1, 0, 0, 1), name='unit box')
nd_box = scene.visuals.Line(pos=box*2-1, color=(0, 1, 0, 1), name='nd box')
vb1.add(unit_box)
vb1.add(nd_box)



if __name__ == '__main__':
    app.run()
