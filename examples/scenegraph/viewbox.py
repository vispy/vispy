"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
from vispy import scenegraph
from vispy import app
from vispy.visuals import transforms
from vispy.scenegraph.entities.viewbox import ViewBox
import numpy as np

canvas = scenegraph.SceneCanvas()
canvas.size = 600, 600
canvas.show()

pos = np.empty((1000,2))
pos[:,0] = np.linspace(-10, 10, 1000)
pos[:,1] = np.random.normal(size=1000)
pos[0] = (0, 0)
pos[1] = (0, 10)
pos[2] = (0, 0)
pos[3] = (20, 0)

box = canvas.root.add_view()

l1 = scenegraph.entities.Line(pos)
l1.transform.scale((50, 50))
l1._visual.set_data(color=(1,0,0,1))
#l1.transform.translate((20, 100))
box.add(l1)

import sys
if sys.flags.interactive == 0:
    app.run()
