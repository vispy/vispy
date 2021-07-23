# -*- coding: utf-8 -*-
# vispy: testskip  # disabled due to segfaults on travis
# vispy: gallery 2
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Multiple Line Views on a Grid 
=============================

Test automatic layout of multiple viewboxes using Grid.
"""

import sys
from vispy import scene
from vispy import app
import numpy as np

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 600, 600
canvas.show()

grid = canvas.central_widget.add_grid()


N = 10000
lines = []
for i in range(10):
    lines.append([])
    for j in range(10):
        vb = grid.add_view(row=i, col=j)
        vb.camera = 'panzoom'
        vb.camera.rect = (0, -5), (100, 10)
        # vb.border = (1, 1, 1, 0.4)

        pos = np.empty((N, 2), dtype=np.float32)
        pos[:, 0] = np.linspace(0, 100, N)
        pos[:, 1] = np.random.normal(size=N)
        line = scene.visuals.Line(pos=pos, color=(1, 1, 1, 0.5), method='gl')
        vb.add(line)


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
