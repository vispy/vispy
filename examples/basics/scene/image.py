# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
from vispy import scene
from vispy import app
import numpy as np

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

img_data = np.random.normal(size=(100, 100, 3), loc=128,
                            scale=50).astype(np.ubyte)

image = scene.visuals.Image(img_data)
image.parent = canvas.scene

# Map image to canvas size with 10px padding
img_bounds = [[0, 0], list(img_data.shape[:2])]
canvas_bounds = [[10, 10], [canvas.size[0] - 10, canvas.size[1] - 10]]
tr = scene.transforms.STTransform.from_mapping(img_bounds, canvas_bounds)
image.transform = tr

import sys
if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
