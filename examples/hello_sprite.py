# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

""" Minimal example demonstrating point sprites.
"""

import time

import numpy as np
from scipy.spatial import cKDTree

from vispy import gl
from vispy import oogl
from vispy import app


# Create texture texture
im1 = np.zeros((100,100,3), 'float64')
im1[:50,:,0] = 1.0
im1[:,:50,1] = 1.0
im1[50:,50:,2] = 1.0

# Create position vector
a_position = np.random.uniform(-1.0, 1.0, (200,2))


VERT_SHADER = """ // sprite vertex shader
#version 120
attribute vec3 a_position;
uniform float u_size;
void main (void) {
    // Calculate position
    gl_Position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
    gl_PointSize = u_size;
}
"""

FRAG_SHADER = """ // sprite fragment shader
#version 120
uniform sampler2D u_texture;
void main()
{   
    gl_FragColor = texture2D(u_texture, gl_PointCoord.xy);
}

"""


class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)
        
        # Create program
        self._program = oogl.ShaderProgram( oogl.VertexShader(VERT_SHADER), 
                                            oogl.FragmentShader(FRAG_SHADER) )
        
        # Set uniforms and attributes
        self._program.uniforms['u_texture'] = oogl.Texture2D(im1)
        self._program.uniforms['u_size'] = 12.0
        self._program.attributes['a_position'] = a_position
    
    
    def on_paint(self, event):
        
        # Set viewport and transformations
        gl.glViewport(0, 0, *self.geometry[2:])
       
        # Clear
        gl.glClearColor(0,0,0,1);
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # todo: normal GL requires these lines, ES 2.0 does not
        from OpenGL import GL
        gl.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(GL.GL_POINT_SPRITE)
        #GL.glTexEnvi(GL.GL_POINT_SPRITE, GL.GL_COORD_REPLACE, GL.GL_TRUE);

        # Draw
        with self._program as prog:
            prog.draw_arrays(gl.GL_POINTS)
        
        # Swap buffers
        self._backend._vispy_swap_buffers()


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
    
