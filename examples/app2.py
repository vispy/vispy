# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

""" More complete example for the app module.
This file also serves as a test for the behavior of the backends.
"""

import time
import random

import vispy
from vispy import app

# Select a backend. Not necessary; Canvas will call app.use() too
# app.use()  # None for auto-select. 'qt', 'PySide', 'PyQt4', 'Glut', 'Pyglet' 

# We'll use pyopengl for the drawing for now
import OpenGL.GL as gl
import OpenGL.GLU as glu

#todo: give mouse events a "buttons" attribute?

class MyCanvas(app.Canvas):
    
    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        
        # Note that args args kwargs are used to initialize the native GUI window
        self.title = 'App demo'
        self.geometry = 50, 50, 300, 300
        
        self._color = 1, 0, 0
        self._mousepos = 0,0
        self.show()
    
    def on_initialize(self, event):
        print('initializing!')
    
    def on_close(self, event):
        print('closing!')
    
    def on_resize(self, event):
        print('Resize %r' % (event.size, ))
    
    
    def on_key_press(self, event):
        if event.key == 'space':
            self.update()
        # Should repeat if held down
        # Note that on GLUT the modifier keys cannot be detected
        modifiers = [key.name for key in event.modifiers]
        print('Key pressed - text: %r, key: %s, modifiers: %r' % (
                event.text, event.key.name, modifiers))
    
    def on_key_release(self, event):
        modifiers = [key.name for key in event.modifiers]
        print('Key released - text: %r, key: %s, modifiers: %r' % (
                event.text, event.key.name, modifiers))
    
    def on_mouse_press(self, event):
        # Should have button: 1: left, 2: right, 3: middle, 4:?
        # Should have pos and modifiers
        # Delta should be 0
        self.print_mouse_event(event, 'Mouse press')
    
    def on_mouse_release(self, event):
        # See mouse press
        self.print_mouse_event(event, 'Mouse release')
    
    def on_mouse_move(self, event):
        # Should print position when over the red square
        # Should always fire, with mouse down and also without
        # Should have pos and modifiers
        # Button and delta should be 0
        if (    event.pos[0] < self.geometry[2]*0.5 
            and event.pos[1] < self.geometry[3]*0.5):
            self.print_mouse_event(event, 'Mouse move')
    
    def on_mouse_wheel(self, event):
        # Should have nonzero delta: -1.0 when scrolling down (as in a browser)
        # Should have pos and modifiers
        # Button should be 0 
        self.print_mouse_event(event, 'Mouse wheel')
    
    def print_mouse_event(self, event, what):
        modifiers = ', '.join([key.name for key in event.modifiers])
        print('%s - pos: %r, button: %i, modifiers: %s, delta: %1.1f' % (
                what, event.pos, event.button, modifiers, event.delta))
    
    
    def on_paint(self, event):
        print('Drawing now (%f)' % time.time())
        
        # Set viewport and transformations
        gl.glViewport(0, 0, *self.geometry[2:])
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluOrtho2D(0.0, 1.0, 0.0, 1.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # Clear
        gl.glClearColor(1,1,1,1);
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # Set color
        gl.glColor(*self._color)
        
        # Draw simple shape
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex(0.0,1.0); 
        gl.glVertex(0.0,0.5); 
        gl.glVertex(0.5,0.5); 
        gl.glVertex(0.5,1.0); 
        gl.glEnd()
        
        self._backend._vispy_swap_buffers()
        
        self.change_color()
    
    def change_color(self, event=None):
        self._color = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)
        #self.update()  # Force redraw


if __name__ == '__main__':
    canvas = MyCanvas()
    
#     # Setup a timer
#     timer = app.Timer(1.0)
#     timer.connect(canvas.change_color)
#     timer.start()
    
    # Enter the mainloop
    app.run()
