#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import sys

from vispy import app
from vispy.gloo import clear

# app.use_app('pyqt4')  # or pyside, glut, pyglet, sdl2, etc.

canvas = app.Canvas(size=(512, 512), title="Do nothing benchmark (vispy)",
                    keys='interactive')


@canvas.connect
def on_draw(event):
    clear(color=True, depth=True)
    canvas.update()  # Draw frames as fast as possible

if __name__ == '__main__':
    canvas.show()
    canvas.measure_fps()
    if sys.flags.interactive == 0:
        app.run()
