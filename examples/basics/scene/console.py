# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demonstrate the use of the vispy console. Note how the console size is
independent of the canvas scaling.
"""

from vispy import scene, app
from vispy.scene.visuals import Console

canvas = scene.SceneCanvas(keys='interactive')
console = Console(color='g', rows=5, parent=canvas.scene)


def on_timer(event):
    if event.iteration % 10 == 0:
        console.clear()
    console.write('Elapsed: %s' % event.elapsed)
    canvas.update()

timer = app.Timer(1.0, connect=on_timer, start=True)

canvas.show()
canvas.app.run()
