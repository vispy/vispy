# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
This example shows how to run from iPython in interactive mode, while 
also updating the VisPy event loop.
"""

import math
from vispy import app, gloo


class Canvas(app.Canvas):

    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.tick = 0
        self.color = (1.0, 1.0, 1.0)

    def on_draw(self, event):
        gloo.clear(color=True)

    def on_timer(self, event):
        # Speed at which the colors animate.
        self.tick += 0.097
        s = abs(0.5 + 0.5 * math.sin(self.tick))
        c = self.color
        gloo.set_clear_color((c[0] * s, c[1] * s, c[2] * s, 1))
        self.update()


# You should run this demo as main with ipython -i <file>
if __name__ == '__main__':
    from vispy.app import set_interactive
    set_interactive()


# All variables listed in this scope are accessible via the console.
canvas = Canvas(keys='interactive')
canvas.show()


# In iPython, try typing the following:
#   > canvas.color = (1.0, 0.0, 0.0)
