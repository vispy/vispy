# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
This example shows how to retrieve event information from a callback.
You should see information displayed for any event you triggered.
"""

from vispy import gloo, app, use
use('pyqt4')  # can be another app backend name


class Canvas(app.Canvas):

    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        self.title = 'App demo'

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
        self.print_mouse_event(event, 'Mouse move')

    def on_mouse_wheel(self, event):
        self.print_mouse_event(event, 'Mouse wheel')

    def print_mouse_event(self, event, what):
        modifiers = ', '.join([key.name for key in event.modifiers])
        print('%s - pos: %r, button: %s, modifiers: %s, delta: %r' %
              (what, event.pos, event.button, modifiers, event.delta))

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)


if __name__ == '__main__':
    canvas = Canvas(keys='interactive')
    canvas.show()
    app.run()
