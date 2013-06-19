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
        
        # Set color and draw shape in that color
        gl.glColor(0.2, 0.0, 0.0)
        self.draw_shape(0,0)
        # Draw shape with texture, the above color should not affect the texture
        with self._texture(0):
            self.draw_shape(0.5, 0.0)
        # Draw shape again, in that above color
        self.draw_shape(0.5,0.5)
        
        self._backend._vispy_swap_buffers()
    
    def draw_shape(self, x, y):
        # Draw simple shape
        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord(0,0); gl.glVertex(x+0,y+0); 
        gl.glTexCoord(0.1,0.8); gl.glVertex(x+0.1,y+0.3); 
        gl.glTexCoord(0.6,1); gl.glVertex(x+0.4,y+0.5); 
        gl.glTexCoord(1,0.1); gl.glVertex(x+0.5,y+0.2); 
        gl.glEnd()
c = Canvas()
c.show()

app.run()
