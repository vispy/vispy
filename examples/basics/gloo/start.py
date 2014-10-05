# !/usr/bin/env python
# -*- coding: utf-8 -*-
""" Probably the simplest vispy example
"""
import sys

from vispy import app, gloo

canvas = app.Canvas(show=True, keys='interactive')


# todo: mmm, either this example should use commands from gloo.gl, or
# we need to make glor.parse() called from the canvas ...

@canvas.connect
def on_draw(event):
    gloo.set_clear_color((0.2, 0.4, 0.6, 1.0))
    gloo.clear()
    gloo.context.get_a_context().glir.parse()

if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
