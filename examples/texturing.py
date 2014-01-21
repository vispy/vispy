# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2

"""
Example demonstrating the use of textures in vispy.gloo.
Three textures are created and combined in the fragment shader.
"""

from vispy.gloo import Program, Texture2D, VertexBuffer
from vispy import app, dataio
from vispy.gloo import gl


import numpy as np

# Texture 1
im1 = dataio.crate()

# Texture with bumbs (to muliply with im1)
im2 = np.ones((20, 20), 'float32')
im2[::3, ::3] = 0.5

# Texture with a plus sign (to subtract from im1)
im3 = np.zeros((30, 30), 'float32')
im3[10, :] = 1.0
im3[:, 10] = 1.0


# Create vetices and texture coords in two separate arrays.
# Note that combining both in one array (as in hello_quad2)
# results in better performance.
positions = np.array([[-0.8, -0.8, 0.0], [+0.7, -0.7, 0.0],
                      [-0.7, +0.7, 0.0], [+0.8, +0.8, 0.0, ]], np.float32)
texcoords = np.array([[1.0, 1.0], [0.0, 1.0],
                      [1.0, 0.0], [0.0, 0.0]], np.float32)


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
        self._program = Program(VERT_SHADER, FRAG_SHADER)

        # Set uniforms and samplers
        self._program['a_position'] = VertexBuffer(positions)
        self._program['a_texcoord'] = VertexBuffer(texcoords)
        #
        self._program['u_texture1'] = Texture2D(im1)
        self._program['u_texture2'] = Texture2D(im2)
        self._program['u_texture3'] = Texture2D(im3)

    def on_initialize(self, event):
        gl.glClearColor(1, 1, 1, 1)

    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)

    def on_paint(self, event):

        # Clear
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Draw shape with texture, nested context
        self._program.draw(gl.GL_TRIANGLE_STRIP)


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
