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

This is what it should look like:

The line in pixel coordinates is normally expected to have the marker
up (since the y-axis points down). The line in 2D unit coordinates is
normally expected to have the marker down (since the y-axis is up). But
positioning a Viewbox is a UnitCamera2 will make it upside down.

  vb1 uses NormalCamera           vb2 uses PixelCamera
  so contents are upside-down     so contents are correct
_______________________________________________________________
|                               |                               |
| long line with marker down    | short line with marker down   |
|_______________________________|_______________________________|
|                               |                               |
| short line with marker up     | long line with marker up      |
|_______________________________|_______________________________|

"""

import numpy as np

from vispy import app
from vispy import scene

#gloo.gl.use('desktop debug')

# <<< Change method here
# With the none method you can see the absence of clipping.
# With the fbo method you can see the texture interpolation (induced by
# a delibirate mismatch in screen and textue resolution)
# Try different combinarions, like a viewport in an fbo
PREFER_PIXEL_GRID1 = 'viewport'  # none, viewport, fbo (fragment to come)
PREFER_PIXEL_GRID2 = 'fbo'


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
canvas.scene.camera = scene.cameras.PixelCamera()

# Create viewboxes left ...

w, h = canvas.size
w2 = w / 2.
h2 = h / 2.

vb1 = scene.ViewBox(canvas.scene, name='vb1', margin=2, border=(1, 0, 0, 1))
vb1.pos = 0, 0
vb1.size = w2, h
vb1.scene.camera = scene.cameras.Fixed2DCamera(fovx=(-1,1))
#
vb11 = scene.ViewBox(vb1.scene, name='vb11', margin=0.02, border=(0, 1, 0, 1))
vb11.pos = -1.0, -1.0
vb11.size = 2.0, 1.0
vb11.scene.camera = scene.cameras.TwoDCamera()
vb11.scene.camera.transform.scale = (2., 2.)
#
vb12 = scene.ViewBox(vb1.scene, name='vb12', margin=0.02, border=(0, 0, 1, 1))
vb12.pos = -1.0, 0.0
vb12.size = 2.0, 1.0
vb12.scene.camera = scene.cameras.PixelCamera()
#vb12.scene.camera.scale = (100, 100)
#
line_ndc.add_parent(vb11.scene)
line_pixels.add_parent(vb12.scene)

box = np.array([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]], dtype=np.float32)
unit_box = scene.visuals.Line(pos=box, color=(1, 0, 0, 1), name='unit box')
nd_box = scene.visuals.Line(pos=box*2-1, color=(0, 1, 0, 1), name='nd box')
vb11.add(unit_box)
vb11.add(nd_box)

# Create viewboxes right ...

vb2 = scene.ViewBox(canvas.scene, name='vb2', margin=2, border=(1, 1, 0, 1))
vb2.pos = w2, 0
vb2.size = w2, h
vb2.scene.camera = scene.cameras.PixelCamera()
#
vb21 = scene.ViewBox(vb2.scene, name='vb21', margin=10, border=(1, 0, 1, 1))
vb21.pos = 0, 0
vb21.size = 400, 300
vb21.scene.camera = scene.cameras.TwoDCamera()
vb21.scene.camera.transform.scale = (2., 2.)
#
vb22 = scene.ViewBox(vb2.scene, name='vb22', margin=10, border=(0, 1, 1, 1))
vb22.pos = 0, 300
vb22.size = 400, 300
vb22.scene.camera = scene.cameras.PixelCamera()
#
line_ndc.add_parent(vb21.scene)
line_pixels.add_parent(vb22.scene)

# Set preferred pixel grid method
for vb in [vb1, vb2]:
    vb.preferred_clip_method = PREFER_PIXEL_GRID1
for vb in [vb11, vb12, vb21, vb22]:
    vb.preferred_clip_method = PREFER_PIXEL_GRID2


# For testing/dev
vb1._name = 'vb1'
vb11._name = 'vb11'
vb12._name = 'vb12'
vb2._name = 'vb2'
vb21._name = 'vb21'
vb22._name = 'vb22'


if __name__ == '__main__':
    app.run()
