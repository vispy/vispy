# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# vispy: gallery 30
"""
Show 10,000 realtime scrolling plots
"""
from vispy import app, scene
import numpy as np


canvas = scene.SceneCanvas(keys='interactive', show=True, size=(1024, 768))
grid = canvas.central_widget.add_grid()
view = grid.add_view(0, 1)
view.camera = scene.MagnifyCamera(mag=1, size_factor=0.5, radius_ratio=0.6)

# Add axes
yax = scene.AxisWidget(orientation='left')
yax.stretch = (0.05, 1)
grid.add_widget(yax, 0, 0)
yax.link_view(view)

xax = scene.AxisWidget(orientation='bottom')
xax.stretch = (1, 0.05)
grid.add_widget(xax, 1, 1)
xax.link_view(view)


N = 4900
M = 2000
cols = int(N**0.5)
view.camera.rect = (0, 0, cols, N/cols)

lines = scene.ScrollingLines(n_lines=N, line_size=M, columns=cols, dx=0.8/M,
                             cell_size=(1, 8), parent=view.scene)
lines.transform = scene.STTransform(scale=(1, 1/8.))


def update(ev):
    m = 50
    data = np.random.normal(size=(N, m), scale=0.3)
    data[data > 1] += 4
    lines.roll_data(data)
    canvas.context.flush()  # prevent memory leak when minimized

timer = app.Timer(connect=update, interval=0)
timer.start()


if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
