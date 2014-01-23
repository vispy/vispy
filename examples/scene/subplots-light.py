"""
Example that illustrates using multiple subplots in a lightweight way
that uses an empty Entity for the transformation of the individual
subplots. There is no clipping.

This example shows that the overhead of glViewPort (as in test_subplot)
can be get rid of if clipping is not necessary. The performance can be
improved further when we introduce a sort of baking approach.

"""

from __future__ import print_function, division, absolute_import

import time
from vispy import scene

from vispy import app

# app.use('glut')

RES = 600
NCOLS = 6
NROWS = 6

# Create a figure
fig = scene.CanvasWithScene()
fig.size = RES, RES
fig.show()

# Add a simple normal pixelcamera. This camera looks at the many
# subplots. Each subplot has its own world with a visual and a camera.
scene.PixelCamera(fig.viewbox)

for col in range(NCOLS):
    for row in range(NROWS):
        # Create "viewbox"
        box = scene.Entity(fig.viewbox)
        box.transform[-1, 0] = col * RES / NCOLS + 100 / NCOLS
        box.transform[-1, 1] = row * RES / NROWS + 100 / NROWS
        box.transform[0, 0] = 1 / NCOLS
        box.transform[1, 1] = 1 / NROWS
        # Create a points visual in the "viewbox"
        points = scene.PointsEntity(box, 100)


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
