""" Example demonstrating showing a quad. Like hello_quad1.py, but now
with Texture2D and VertexBuffer.
"""

import time
import numpy as np

from vispy.oogl import Texture2D, VertexBuffer, ElementBuffer
from vispy.oogl import VertexShader, FragmentShader, ShaderProgram
from vispy import app
from vispy import gl


# Create a texture
im1 = np.zeros((100,100,3), 'float64')
im1[:50,:,0] = 1.0
im1[:,:50,1] = 1.0
im1[50:,50:,2] = 1.0

# Create vetices and texture coords, combined in one array for high performance
vertex_data = np.zeros(4, dtype=[('pos', np.float32, 3), ('texcoord', np.float32, 2) ])
vertex_data['pos'] = np.array([ [-0.8, -0.8, 0.0], [+0.7, -0.7, 0.0],  
                                [-0.7, +0.7, 0.0], [+0.8, +0.8, 0.0,] ])
vertex_data['texcoord'] = np.array([    [0.0, 0.0], [0.0, 1.0], 
                                        [1.0, 0.0], [1.0, 1.0] ])


VERT_SHADER = """ // simple vertex shader

attribute vec3 vPosition;
attribute vec2 vTexcoord;
uniform float sizeFactor;
//attribute float sizeFactor;

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
        
        # Create program
        self._program = ShaderProgram(
                VertexShader(VERT_SHADER), FragmentShader(FRAG_SHADER) )
        
        # Set uniforms, samplers, attributes
        # We create one VBO with all vertex data (array of structures)
        # and create two views from it for the attributes.
        self._program.uniforms.texture1 = Texture2D(im1)
        self._vbo = VertexBuffer(vertex_data)
        self._program.attributes.vPosition = self._vbo['pos']
        self._program.attributes.vTexcoord = self._vbo['texcoord']
    
    def on_paint(self, event):
        
        # Set viewport and transformations
        gl.glViewport(0, 0, *self.geometry[2:])
        
        # Clear
        gl.glClearColor(1,1,1,1);
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # Draw
        with self._program as prog:
            # You can set uniforms/attributes here too
            prog.uniforms.sizeFactor = 0.5 + np.sin(time.time()*3)*0.2
            #prog.attributes.sizeFactor = 0.5 + np.sin(time.time()*3)*0.2
           
            # Draw
            gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)
            
        self._backend._vispy_swap_buffers()
        self.update()


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
