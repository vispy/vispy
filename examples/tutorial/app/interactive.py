# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
This example shows how to configure VisPy to run from IPython (or Python) in
interactive mode, while simultaneously updating the VisPy event loop.  This
behavior is supported by default in all code that calls vispy.app.run(), but
here it's setup manually.

Run this file with `ipython -i interactive.py` to get a console and a window.
"""

import math
from vispy import app, gloo
from vispy.color import Color


class Canvas(app.Canvas):

    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.color = 'white'

    def on_draw(self, event):
        gloo.clear(color=True)

    def on_timer(self, event):
        # Animation speed based on global time.
        t = event.elapsed
        c = Color(self.color).rgb
        # Simple sinusoid wave animation.
        s = abs(0.5 + 0.5 * math.sin(t))
        self.context.set_clear_color((c[0] * s, c[1] * s, c[2] * s, 1))
        self.update()


# You should run this demo as main with ipython -i <file>.  If interactive
# mode is not specified, this demo will exit immediately because this demo
# doesn't call run and relies on the input hook being setup.
if __name__ == '__main__':
    from vispy import app
    # app.use_app('glfw')  # for testing specific backends
    app.set_interactive()


# All variables listed in this scope are accessible via the console.
canvas = Canvas(keys='interactive')
canvas.show()


# In IPython, try typing any of the following:
#   >>> canvas.color = (1.0, 0.0, 0.0)
#   >>> canvas.color = 'red'
