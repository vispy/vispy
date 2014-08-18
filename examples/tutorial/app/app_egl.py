#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This example shows how to actively select and test the egl backend.

You should see a black window and any mouse or keyboard event should be
detected. A timer is also run every second and it should print "tick !"
every second.
"""

from vispy import app, use, gloo
use('egl')


class Canvas(app.Canvas):

    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        timer = app.Timer(0.01)
        timer.connect(self.on_timer)
        timer.start()
        self.i = 0

    def on_initialize(self, event):
        gloo.set_clear_color('black')
        print('on_initialize')

    def on_close(self, event):
        print('on_close')

    def on_draw(self, event):
        print('on_draw')
        gloo.clear(color=True, depth=True)

    def on_timer(self, event):
        self.i += 1
        print('tick !')
        if self.i >= 10:
            self.close()

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    canvas = Canvas(keys='interactive')
    canvas.show()
    app.run()
