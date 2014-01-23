# !/usr/bin/env python
# -*- coding: utf-8 -*-
""" Probably the simplest vispy example
"""

from vispy import app
from vispy.gloo import gl

c = app.Canvas(show=True)


@c.connect
def on_paint(event):
    gl.glClearColor(0.2, 0.4, 0.6, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

if __name__ == '__main__':
    app.run()
