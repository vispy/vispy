"""
Simple test showing one entity.
It also illustrates using a hierarchy of entities to easily transform
objects. Similarly, the camera can be positioned by transforming a parent
object. Further, this example runs an FPS counter.
"""

import time
from vispy import scene

from vispy import app

# app.use('glut')

# Create a figure
fig = scene.CanvasWithScene()
fig.size = 600, 600
fig.show()


# Create a camera inside a container
camcontainer = scene.PixelCamera(fig.viewbox)
camera = scene.TwoDCamera(camcontainer)
camera.xlim = -100, 500
camera.ylim = -100, 500


# Explicitly set the second camera, or the ViewBox will pick the second
fig.viewbox.camera = camera

# Create a points entity inside a container
pointscontainer = scene.Entity(fig.viewbox)
points = scene.PointsEntity(pointscontainer, 1000)

# Transform either the camera container or the point container.
# Their effects should be mutually reversed.
# UNCOMMENT TO ACTIVATE
#
#transforms.translate(camcontainer.transform, 50, 50)
#transforms.rotate(camcontainer.transform, 10, 0,0,1)
#
#transforms.translate(pointscontainer.transform, 50, 50)
#transforms.rotate(pointscontainer.transform, 10, 0,0,1)


# Count FPS
t0, frames, t = time.time(), 0, 0


@fig.connect
def on_paint(event):
    global t, t0, frames
    t = time.time()
    frames = frames + 1
    elapsed = (t - t0)  # seconds
    if elapsed > 2.5:
        print("FPS : %.2f (%d frames in %.2f second)"
              % (frames / elapsed, frames, elapsed))
        t0, frames = t, 0
    event.source.update()

# Run!
app.run()
