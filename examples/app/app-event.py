# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This example shows how to retrieve event information from a callback.
You should see information displayed for any event you triggered.
"""

import vispy.gloo.gl as gl
import vispy.app as app


class Canvas(app.Canvas):

    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self.title = 'App demo'

    def on_initialize(self, event):
        print('initializing!')

    def on_close(self, event):
        print('closing!')

    def on_resize(self, event):
        print('Resize %r' % (event.size, ))

    def on_key_press(self, event):
        modifiers = [key.name for key in event.modifiers]
        print('Key pressed - text: %r, key: %s, modifiers: %r' % (
            event.text, event.key.name, modifiers))

    def on_key_release(self, event):
        modifiers = [key.name for key in event.modifiers]
        print('Key released - text: %r, key: %s, modifiers: %r' % (
            event.text, event.key.name, modifiers))

    def on_mouse_press(self, event):
        self.print_mouse_event(event, 'Mouse press')

    def on_mouse_release(self, event):
        self.print_mouse_event(event, 'Mouse release')

    def on_mouse_move(self, event):
        if (event.pos[0] < self.size[0] * 0.5
                and event.pos[1] < self.size[1] * 0.5):
            self.print_mouse_event(event, 'Mouse move')

    def on_mouse_wheel(self, event):
        self.print_mouse_event(event, 'Mouse wheel')

    def print_mouse_event(self, event, what):
        modifiers = ', '.join([key.name for key in event.modifiers])
        print('%s - pos: %r, button: %i, modifiers: %s, delta: %r' %
              (what, event.pos, event.button, modifiers, event.delta))

    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)


if __name__ == '__main__':
    canvas = Canvas()
    canvas.show()
    app.run()
