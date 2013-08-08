# #!/usr/bin/env python
# -*- coding: utf-8 -*-

from vispy import app
app.use('qt')

class Canvas(app.Canvas):
    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)

    def on_initialize(self, event):
        print('on_initialize')

    def on_close(self, event):
        print('on_close')

    def on_resize(self, event):
        print('on_resize (%dx%d)' % event.size)

    def on_key_press(self, event):
        print('on_key_press: %s' % event.text)

    def on_key_release(self, event):
        print('on_key_release')

    def on_mouse_press(self, event):
        print('on_mouse_press: %d' % event.button)

    def on_mouse_release(self, event):
        print('on_mouse_release')

    def on_mouse_move(self, event):
        print('on_mouse_move (%dx%d)' % event.pos)

    def on_mouse_wheel(self, event):
        print('on_mouse_wheel: %d' % event.delta)
        
    def on_paint(self, event):
        print('on_paint')
    
if __name__ == '__main__':
    canvas = Canvas()
    canvas.show()
    app.run()
