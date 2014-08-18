# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 20

"""
This is a very minimal example that opens a window and makes the background
color to change from black to white to black ...

The backend (one of 'qt', 'glut', 'pyglet') is chosen automatically depending
on what is available on your machine.
"""

import math
from vispy import app, gloo


class Canvas(app.Canvas):

    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        timer = app.Timer(1 / 60.0)
        timer.connect(self.on_timer)
        timer.start()
        self.tick = 0

    def on_draw(self, event):
        gloo.clear(color=True)

    def on_timer(self, event):
        self.tick += 1 / 60.0
        c = abs(math.sin(self.tick))
        gloo.set_clear_color((c, c, c, 1))
        self.update()

    def show_fps(self, fps):
        print("FPS - %.2f" % fps)

if __name__ == '__main__':
    canvas = Canvas(keys='interactive')
    canvas.show()
    canvas.measure_fps(1, canvas.show_fps)
    app.run()
