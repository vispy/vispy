# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

""" Example demonstrating the use of textures in vispy.oogl
Three textures are created and combined in the fragment shader.
The code for this example is in the public domain.
"""

from vispy.oogl import Texture2D, VertexBuffer, ElementBuffer
from vispy.oogl import VertexShader, FragmentShader, ShaderProgram
from vispy import app
from vispy import gl

import numpy as np

# Texture with four quadrants in different colors
im1 = np.zeros((100,100,3), 'uint8') # Note the use of clim later
im1[:50,:,0] = 1.0
im1[:,:50,1] = 1.0
im1[50:,50:,2] = 1.0

# Texture with bumbs (to muliply with im1)
im2 = np.ones((20,20), 'float32')
im2[::3,::3] = 0.7

# Texture with a plus sign (to subtract from im1)
im3 = np.zeros((30,30), 'float32')
im3[10,:] = 1.0
im3[:,10] = 1.0


# Create vetices and texture coords in two separate arrays.
# Note that combining both in one array (as in hello_quad2)
# results in better performance.
positions = np.array([  [-0.8, -0.8, 0.0], [+0.7, -0.7, 0.0],  
                        [-0.7, +0.7, 0.0], [+0.8, +0.8, 0.0,] ])
texcoords = np.array([  [0.0, 0.0], [0.0, 1.0], 
                        [1.0, 0.0], [1.0, 1.0] ])


VERT_SHADER = """ // texture vertex shader

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

FRAG_SHADER = """ // texture fragment shader
uniform sampler2D u_texture1;
uniform sampler2D u_texture2;
uniform sampler2D u_texture3;

varying vec2 v_texcoord;

void main()
{    
    vec4 clr1 = texture2D(u_texture1, v_texcoord);
    vec4 clr2 = texture2D(u_texture2, v_texcoord);
    vec4 clr3 = texture2D(u_texture3, v_texcoord);
    gl_FragColor.rgb = clr1.rgb * clr2.r - clr3.r;
    gl_FragColor.a = 1.0;
}
"""



class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)
        
        # Create program
        self._program = ShaderProgram(
                VertexShader(VERT_SHADER), 
                FragmentShader(FRAG_SHADER),
                )
        
        # Set uniforms and samplers
        self._program.attributes['a_position'] = VertexBuffer(positions)
        self._program.attributes['a_texcoord'] = VertexBuffer(texcoords)
        #
        self._program.uniforms['u_texture1'] = Texture2D(im1, clim=(0,1))
        self._program.uniforms['u_texture2'] = Texture2D(im2)
        self._program.uniforms['u_texture3'] = Texture2D(im3)
    
    
    def on_paint(self, event):
        
        # Set viewport and transformations
        gl.glViewport(0, 0, *self.geometry[2:])
        
        # Clear
        gl.glClearColor(1,1,1,1);
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # Draw shape with texture, nested context
        with self._program as prog:
            prog.draw_arrays(gl.GL_TRIANGLE_STRIP)
        
        # Swap buffers
        self._backend._vispy_swap_buffers()


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
