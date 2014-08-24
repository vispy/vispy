#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from vispy import app, use
from vispy.gloo import clear

# use('pyqt4')  # or pyside, glut, pyglet, sdl2, etc.

canvas = app.Canvas(size=(512, 512), title = "Do nothing benchmark (vispy)",
                    keys='interactive')

@canvas.connect
def on_draw(event):
    clear(color=True, depth=True)
    canvas.update()  # Draw frames as fast as possible

canvas.show()
canvas.measure_fps()
app.run()
