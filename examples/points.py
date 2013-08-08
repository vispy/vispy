# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

""" Simple example plotting 2D points.
"""

from vispy import oogl
from vispy import app
from vispy import gl
from OpenGL import GL
import numpy as np

# Create vetices 
npoints = 100000
v_position = .25 * np.random.randn(npoints, 2).astype(np.float32)
v_color = np.random.rand(npoints, 3).astype(np.float32)

VERT_SHADER = """ // simple vertex shader
attribute vec3 a_position;
attribute vec3 a_color;
varying vec3 v_color;
void main (void) {
    gl_Position = vec4(a_position, 1.0);
    v_color = a_color;
}
"""

FRAG_SHADER = """ // simple fragment shader
varying vec3 v_color;
void main()
{    
    gl_FragColor = vec4(v_color, .25);
}
"""

class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self)
        # Create program
        self._program = oogl.ShaderProgram( oogl.VertexShader(VERT_SHADER), 
                                            oogl.FragmentShader(FRAG_SHADER) )
        # Set uniform and attribute
        self._program.attributes['a_color'] = v_color
        self._program.attributes['a_position'] = v_position
    
    def on_paint(self, event):
        # Set viewport and transformations
        gl.glViewport(0, 0, *self.geometry[2:])
        # Clear
        gl.glClearColor(0, 0, 0, 0);
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Enable transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
        # Enable point sprites (allow to change the size of the points with
        # gl_PointSize in the vertex shader)
        gl.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(GL.GL_POINT_SPRITE)
        # Draw
        with self._program as prog:
            prog.draw_arrays(gl.GL_POINTS)
        # Swap buffers
        self._backend._vispy_swap_buffers()

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
