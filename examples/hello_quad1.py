""" Simple example demonstrating showing a quad.
oogl objects that this example demonstrates: ShaderProgram.
"""

from vispy.oogl import VertexShader, FragmentShader, ShaderProgram
from vispy import app
from vispy import gl
import numpy as np

# Create vetices and texture coords
vPosition = np.array([  -0.8,-0.8,0.0,  +0.7,-0.7,0.0,  
                        -0.7,+0.7,0.0,  +0.8,+0.8,0.0,], np.float32)
vPosition.shape = -1,3


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
        
        # Set uniforms
        self._program.set_uniform('color', (0.2, 1.0, 0.4, 1.0))
    
    def on_paint(self, event):
        
        # Set viewport and transformations
        gl.glViewport(0, 0, *self.geometry[2:])
        
        # Clear
        gl.glClearColor(1,1,1,1);
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        with self._program:
            
            # Set vertices
            L1 = self._program.get_attribute_location('vPosition')
            if L1 >= 0:
                gl.glVertexAttribPointer(L1, vPosition.shape[1], 
                                        gl.GL_FLOAT, gl.GL_FALSE, 0, vPosition)
                gl.glEnableVertexAttribArray(L1)
                gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, len(vPosition))
        
        self._backend._vispy_swap_buffers()
    

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
