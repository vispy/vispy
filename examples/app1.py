# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

""" Example demonstrating the use of the vispy.app module. 
More specifically, this demo shows how to select a backend, and
how to use the Canvas, and Timer classes. 
"""
import time
import random

import vispy
from vispy import app

# Select a backend
# This bit would have to become more smart/flexible when used without argument:
# 1) if one of the backend is already imported, it should use that
# 2) it should be possible to specify a default backend in a config file

app.use('qt')
# app.use('glut')
# app.use('pyglet')

# We'll use pyopengl for the drawing for now
import OpenGL.GL as gl
import OpenGL.GLU as glu


class MyCanvas(app.Canvas):
    
    def __init__(self, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        
        # Note that args args kwargs are used to initialize the native GUI window
        self.title = 'App demo'
        self.geometry = 50, 50, 300, 300
        
        self._color = 1, 0, 0
        
        self.show()
        
    def on_close(self, event):
        print('closing!')
    
    def on_paint(self, event):
        # 
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
        gl.glTexCoord(0,0); gl.glVertex(0,0); 
        gl.glTexCoord(0.1,0.8); gl.glVertex(0.2,0.7); 
        gl.glTexCoord(0.6,1); gl.glVertex(0.8,1); 
        gl.glTexCoord(1,0.1); gl.glVertex(1,0.2); 
        gl.glEnd()
        
        self._backend._vispy_swap_buffers()
    
    def change_color(self, event):
        self._color = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)
        self.update()  # Force redraw


if __name__ == '__main__':
    canvas = MyCanvas()
    
    # Setup a timer
    timer = app.Timer(1.0)
    timer.connect(canvas.change_color)
    timer.start()
    
    # Enter the mainloop
    app.run()
        