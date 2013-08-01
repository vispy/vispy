# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

""" Minimal example demonstrating the use of frame buffer objects (VBO).
"""


from vispy import oogl
from vispy import app
from vispy import gl
import numpy as np

# Create vetices 
vPosition = np.array([  [-0.8, -0.8, 0.0],  [+0.7, -0.7, 0.0],  
                        [-0.7, +0.7, 0.0],  [+0.8, +0.8, 0.0,] ], np.float32)
vTexcoord = np.array([  [0.0, 0.0], [0.0, 1.0], 
                        [1.0, 0.0], [1.0, 1.0] ], np.float32)

# For initial quad
VERT_SHADER1 = """ // simple vertex shader
attribute vec3 a_position;
void main (void) {
    gl_Position = vec4(a_position, 1.0);
}
"""

FRAG_SHADER1 = """ // simple fragment shader
uniform vec4 u_color;
void main()
{    
    gl_FragColor = u_color;
}
"""

# To render the result of the FBO
VERT_SHADER2 = """ // textured vertex shader

attribute vec3 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;
void main (void) {
    // Pass tex coords
    v_texcoord = a_texcoord;
    // Calculate position
    gl_Position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
}
"""

FRAG_SHADER2 = """ // textured fragment shader
uniform sampler2D u_texture1;
varying vec2 v_texcoord;
void main()
{    
    gl_FragColor = texture2D(u_texture1, v_texcoord.st);
}

"""


SIZE = 50

class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)
        
        # Create texture to render to
        self._rendertex = oogl.Texture2D()
        
        # Create FBO, attach the color buffer and depth buffer
        self._fbo = oogl.FrameBuffer()
        self._fbo.attach_color(self._rendertex)
        self._fbo.attach_depth(oogl.RenderBuffer())
        
        # Create program to render a shape
        self._program1 = oogl.ShaderProgram(
                oogl.VertexShader(VERT_SHADER1), oogl.FragmentShader(FRAG_SHADER1) )
        self._program1.uniforms.u_color = 0.9, 1.0, 0.4, 1
        self._program1.attributes.a_position = vPosition
        
        # Create program to render FBO result
        self._program2 = oogl.ShaderProgram(
                oogl.VertexShader(VERT_SHADER2), oogl.FragmentShader(FRAG_SHADER2) )
        self._program2.attributes.a_position = vPosition
        self._program2.attributes.a_texcoord = vTexcoord
        self._program2.uniforms.u_texture1 = self._rendertex
    
    
    def on_paint(self, event):
        
        # Set shape of fbo to match screen
        shape = self.geometry[2:] + (3,)  # todo: x/y swap
        self._fbo.set_shape(shape)
        
        with self._program1 as prog:
            with self._fbo:
                # Set viewport and transformations
                gl.glViewport(0, 0, *shape[:2])
                gl.glClearColor(0,0.0,0.5,1);
                gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
                # Draw
                prog.draw_arrays(gl.GL_TRIANGLE_STRIP)
        
        with self._program2 as prog:
            # Set viewport and transformations
            gl.glViewport(0, 0, *self.geometry[2:])
            gl.glClearColor(1,1,1,1);
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            # Draw
            prog.draw_arrays(gl.GL_TRIANGLE_STRIP)
        
        # Swap buffers
        self._backend._vispy_swap_buffers()
    

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()