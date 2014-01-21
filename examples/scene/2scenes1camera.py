""" Test the display of two different scenes using the same camera.
This can for instance be useful to view two representations
of the same data (e.g. an image and its segmentation).

This example illustrates:
  * Having two viewboxes that show different scenes
  * Using the same camera in both scenes, via multiple parenting
"""

from vispy import scene

from vispy import app
from vispy.util import transforms


# Create figure with one pixel camera
fig = scene.CanvasWithScene()
fig.size = 800, 400
fig.show()
camera = scene.PixelCamera(fig.viewbox)
#


@fig.connect
def on_mouse_move(event):
    cam0.on_mouse_move(event)

# Create two viewboxes
vp1 = scene.ViewBox(fig.viewbox)
vp2 = scene.ViewBox(fig.viewbox)
vp1.bgcolor = (0, 0, 0.2)
vp2.bgcolor = (0, 0.2, 0)

# Put them next to each-other
transforms.scale(vp1.transform, 400, 400)
transforms.scale(vp2.transform, 400, 400)
transforms.translate(vp1.transform, 0)
transforms.translate(vp2.transform, 400, 0, 0)

# Create one object in each scene
points1 = scene.PointsEntity(vp1, 100)
points2 = scene.PointsEntity(vp2, 1000)

# Create a camera
cam0 = scene.TwoDCamera()
cam0.parents = vp1, vp2

# Set limits of cam0, this is only to set position right, its fov is not used
cam0.xlim = -100, 500
cam0.ylim = -100, 500

app.run()
