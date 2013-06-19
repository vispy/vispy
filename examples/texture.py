from vispy.oogl import Texture2D
from vispy import app
import OpenGL.GL as gl
import OpenGL.GLU as glu
import numpy as np

im = np.zeros((100,100,3), 'float64')
im[:50,:,0] = 1.0
im[:,:50,1] = 1.0
im[50:,50:,2] = 1.0

class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)
        
        self._texture = Texture2D()
        self._texture.set_data(im)
        
        
    def on_paint(self, event):
        # 
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
        gl.glColor(1.0, 1.0, 1.0)
        with self._texture:
            # Draw simple shape
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord(0,0); gl.glVertex(0,0); 
            gl.glTexCoord(0.1,0.8); gl.glVertex(0.2,0.7); 
            gl.glTexCoord(0.6,1); gl.glVertex(0.8,1); 
            gl.glTexCoord(1,0.1); gl.glVertex(1,0.2); 
            gl.glEnd()
        
        self._backend._vispy_swap_buffers()

c = Canvas()
c.show()

app.run()
