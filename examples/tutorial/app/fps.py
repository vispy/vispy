# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
This is a very minimal example that opens a window and makes the background
color to change from black to white to black ...

The backend is chosen automatically depending on what is available on
your machine.
"""

import math
import time

from vispy import app


class Canvas(app.Canvas):

    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self.show()

    def on_draw(self, event):
        c = 0.5 + math.sin(math.pi * time.time()) / 2.
        self.context.clear([c] * 3)
        self.update()

if __name__ == '__main__':
    canvas = Canvas(keys='interactive', vsync=False)
    canvas.measure_fps()
    app.run()
