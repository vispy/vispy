# !/usr/bin/env python
# -*- coding: utf-8 -*-
""" Probably the simplest vispy example
"""

from vispy import app
from vispy import gloo

c = app.Canvas(show=True, close_keys='escape')


@c.connect
def on_draw(event):
    gloo.set_clear_color((0.2, 0.4, 0.6, 1.0))
    gloo.clear()

if __name__ == '__main__':
    app.run()
