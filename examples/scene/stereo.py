""" Test stereoscopic display.

This example illustrates:
  * Having two viewboxes that show the same scene
  * Using a different camera for each viewbox
  * Controlling both cameras simultaneously
"""

from vispy import scene

from vispy import app
from vispy.util import transforms


class MyFigure(scene.CanvasWithScene):

    def on_mouse_move(self, event):
        cam0.on_mouse_move(event)
#         cam2.on_mouse_move(event)

# Create figure with one pixel camera
fig = MyFigure()  # scene.Figure()
fig.size = 800, 400
fig.show()
#camera = scene.NDCCamera(fig.viewvbox)
camera = scene.PixelCamera(fig.viewbox)

# Create two viewbox, use the same scene
vp1 = scene.ViewBox(fig.viewbox)
vp2 = scene.ViewBox(fig.viewbox)

# Put them next to each-other
transforms.scale(vp1.transform, 400, 400)
transforms.scale(vp2.transform, 400, 400)
transforms.translate(vp1.transform, 0)
transforms.translate(vp2.transform, 400, 0, 0)

# Create a world object to act as a container
# It is a child of both viewports
world = scene.Entity()
world.parents = vp1, vp2

# Create two cameras
cam0 = scene.TwoDCamera(world)  # Placeholder camera
cam1 = scene.TwoDCamera(cam0)
cam2 = scene.TwoDCamera(cam0)

# Set limits of cam0, this is only to set position right, its fov is not used
cam0.xlim = -100, 500
cam0.ylim = -100, 500

# Set fov of cam1 and cam2, and translate both cameras a bit
cam1.fov = cam2.fov = 600, 600
transforms.translate(cam1.transform, -50, 0)
transforms.translate(cam2.transform, +50, 0)

# Apply cameras
vp1.camera = cam1
vp2.camera = cam2
vp1.bgcolor = (0, 0, 0.2)
vp2.bgcolor = (0, 0.2, 0)

# Create a entity
points = scene.PointsEntity(world)

app.run()
