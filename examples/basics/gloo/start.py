# !/usr/bin/env python
# -*- coding: utf-8 -*-
""" Probably the simplest vispy example
"""
import sys

from vispy import app, gloo

canvas = app.Canvas(keys='interactive')


@canvas.connect
def on_draw(event):
    gloo.set_clear_color((0.2, 0.4, 0.6, 1.0))
    gloo.clear()

canvas.show()

if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
