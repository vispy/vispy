""" Simple example demonstrating showing a textured quad.
"""

from vispy.oogl import Texture2D, VertexShader, FragmentShader, ShaderProgram
from vispy import app
from vispy import gl
import numpy as np

# Create a texture
im1 = np.zeros((100,100,3), 'float64')
im1[:50,:,0] = 1.0
im1[:,:50,1] = 1.0
im1[50:,50:,2] = 1.0

# Create vetices and texture coords
vPosition = np.array([  -0.8,-0.8,0.0,  +0.7,-0.7,0.0,  
                        -0.7,+0.7,0.0,  +0.8,+0.8,0.0,], np.float32)
vTexcoords = np.array([  0.0,0.0,  0.0,1.0, 1.0,0.0,  1.0,1.0], np.float32)
vPosition.shape = -1,3
vTexcoords.shape = -1,2


VERT_SHADER = """ // simple vertex shader

attribute vec3 vPosition;
attribute vec2 vTexcoord;
uniform float sizeFactor;

void main (void) {
    // Pass tex coords
    gl_TexCoord[0] = vec4(vTexcoord.x, vTexcoord.y, 0.0, 0.0);
    // Calculate position
    gl_Position = sizeFactor*vec4(vPosition.x, vPosition.y, vPosition.z,
                                                        1.0/sizeFactor);
}
"""

FRAG_SHADER = """ // simple fragment shader
uniform sampler2D texture1;

void main()
{    
    gl_FragColor = texture2D(texture1, gl_TexCoord[0].st);
}

"""


class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)
        
        # Create texture 1
        self._texture1 = Texture2D()
        self._texture1.set_data(im1)
        
        # Create program
        self._program = ShaderProgram(
                VertexShader(VERT_SHADER), FragmentShader(FRAG_SHADER) )
        
        # Set uniforms
        self._program.set_uniform('texture1', self._texture1)
        self._program.set_uniform('sizeFactor', 0.6)
    
    def on_paint(self, event):
        
        # Set viewport and transformations
        gl.glViewport(0, 0, *self.geometry[2:])
        
        # Clear
        gl.glClearColor(1,1,1,1);
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        with self._texture1(0), self._program:
            
            # Set vertices
            L1 = self._program.get_attribute_location('vPosition')
            if L1 >= 0:
                gl.glVertexAttribPointer(L1, vPosition.shape[1], 
                                        gl.GL_FLOAT, gl.GL_FALSE, 0, vPosition)
                gl.glEnableVertexAttribArray(L1)
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, len(vPosition))
            
            # Set texture coords
            L2 = self._program.get_attribute_location('vTexcoord')
            if L2 >= 0:
                gl.glVertexAttribPointer(L2, vTexcoords.shape[1],
                                        gl.GL_FLOAT, gl.GL_FALSE, 0, vTexcoords)
                gl.glEnableVertexAttribArray(L2)
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, len(vTexcoords))
        
        self._backend._vispy_swap_buffers()
    

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
