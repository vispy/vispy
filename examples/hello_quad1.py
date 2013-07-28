""" Simple example demonstrating showing a quad.
oogl objects that this example demonstrates: ShaderProgram.
"""

from vispy.oogl import VertexShader, FragmentShader, ShaderProgram
from vispy import app
from vispy import gl
import numpy as np

# Create vetices 
vPosition = np.array([  [-0.8, -0.8, 0.0],  [+0.7, -0.7, 0.0],  
                        [-0.7, +0.7, 0.0],  [+0.8, +0.8, 0.0,] ], np.float32)


VERT_SHADER = """ // simple vertex shader
attribute vec3 vPosition;
void main (void) {
    gl_Position = vec4(vPosition, 1.0);
}
"""

FRAG_SHADER = """ // simple fragment shader
uniform vec4 color;
void main()
{    
    gl_FragColor = color;
}
"""


class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)
        
        # Create program
        self._program = ShaderProgram(
                VertexShader(VERT_SHADER), FragmentShader(FRAG_SHADER) )
        
        # Set uniform and attribute
        self._program.uniforms.color = 0.2, 1.0, 0.4, 1
        self._program.attributes.vPosition = vPosition
    
    
    def on_paint(self, event):
        
        # Set viewport and transformations
        gl.glViewport(0, 0, *self.geometry[2:])
        
        # Clear
        gl.glClearColor(1,1,1,1);
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # Draw
        with self._program as prog:
            prog.draw_arrays(gl.GL_TRIANGLE_STRIP)
        
        # Swap buffers
        self._backend._vispy_swap_buffers()
    

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
