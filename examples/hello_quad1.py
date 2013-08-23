# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

""" 
Simple example demonstrating showing a quad.
oogl objects that this example demonstrates: ShaderProgram.
"""

from vispy import oogl
from vispy import app
from vispy import gl
import numpy as np

# Create vetices 
vPosition = np.array([  [-0.8, -0.8, 0.0],  [+0.7, -0.7, 0.0],  
                        [-0.7, +0.7, 0.0],  [+0.8, +0.8, 0.0,] ], np.float32)


VERT_SHADER = """ // simple vertex shader
attribute vec3 a_position;
void main (void) {
    gl_Position = vec4(a_position, 1.0);
}
"""

FRAG_SHADER = """ // simple fragment shader
uniform vec4 u_color;
void main()
{    
    gl_FragColor = u_color;
}
"""


class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)
        
        # Create program
        self._program = oogl.ShaderProgram( oogl.VertexShader(VERT_SHADER), 
                                            oogl.FragmentShader(FRAG_SHADER) )
        
        # Set uniform and attribute
        self._program.uniforms['u_color'] = 0.2, 1.0, 0.4, 1
        self._program.attributes['a_position'] = vPosition
    
    
    def on_initialize(self, event):
        gl.glClearColor(1,1,1,1)
    
    
    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
    
    
    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        with self._program as prog:
            prog.draw_arrays(gl.GL_TRIANGLE_STRIP)
    

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
