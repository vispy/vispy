# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

""" Example demonstrating simulating fireworks using point sprites.
This example was taken from the gold book. 

It demonstrates a series of explosions that each last 1 second. The
visualization during the explostion is highly optimized, e.g. using a
VBO. After each explosion, the vertex data for the next explosion 
are calculated, so each explostion is unique.
"""

import time
import numpy as np

from vispy import oogl
from vispy import app
from vispy import gl

# Create a texture
radius = 32
im1 = np.random.normal(0.8, 0.3, (radius*2+1, radius*2+1))
# Mask it with a disk
L = np.linspace(-radius, radius, 2 * radius + 1)
(X, Y) = np.meshgrid(L, L)
im1 *= np.array((X**2 + Y**2) <= radius * radius, dtype='float32')

# Set number of particles, you should be able to scale this to 100000
N = 10000

# Create vertex data container
vertex_data = np.zeros((N,), dtype=[('a_lifetime', np.float32, 1),
                                    ('a_startPosition', np.float32, 3),
                                    ('a_endPosition', np.float32, 3)])


VERT_SHADER = """ // explosion vertex shader
#ifndef GL_ES
#version 120
#endif

uniform float u_time;
uniform vec3 u_centerPosition;
attribute float a_lifetime;
attribute vec3 a_startPosition;
attribute vec3 a_endPosition;
varying float v_lifetime;

void main () {
    if (u_time <= a_lifetime)
    {
        gl_Position.xyz = a_startPosition + (u_time * a_endPosition);
        gl_Position.xyz += u_centerPosition;
        gl_Position.w = 1.0;
    }
    else
        gl_Position = vec4(-1000, -1000, 0, 0);
    
    v_lifetime = 1.0 - (u_time / a_lifetime);
    v_lifetime = clamp(v_lifetime, 0.0, 1.0);
    gl_PointSize = (v_lifetime * v_lifetime) * 40.0;
}
"""

FRAG_SHADER = """ // explostion fragment shader
#ifndef GL_ES
#version 120
#endif

uniform sampler2D texture1;
uniform vec4 u_color;
varying float v_lifetime;
uniform sampler2D s_texture;

void main()
{    
    vec4 texColor;
    texColor = texture2D(s_texture, gl_PointCoord);
    gl_FragColor = vec4(u_color) * texColor;
    gl_FragColor.a *= v_lifetime;
}
"""


class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)
        
        # Create program
        self._program = oogl.ShaderProgram( oogl.VertexShader(VERT_SHADER), 
                                            oogl.FragmentShader(FRAG_SHADER) )
        
        # Create vbo
        self._vbo = oogl.VertexBuffer(vertex_data)
        
        # Set uniforms, samplers, attributes
        self._program.attributes.update(self._vbo)
        self._program.uniforms['s_texture'] = oogl.Texture2D(im1)
        
        # Create first explosion
        self._new_explosion()
    
    
    def on_initialize(self, event):
        gl.glClearColor(0,0,0,1);
        
        # Enable blending
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
        
        # todo: normal GL requires these lines, ES 2.0 does not
        from OpenGL import GL
        gl.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(GL.GL_POINT_SPRITE)
    
    
    def on_paint(self, event):
        
        # Set viewport and clear buffer
        gl.glViewport(0, 0, *self.geometry[2:])
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # Draw
        with self._program as prog:
            prog.uniforms['u_time'] = time.time() - self._starttime
            prog.draw_arrays(gl.GL_POINTS)
        
        # Swap buffers and invoke a new draw
        self._backend._vispy_swap_buffers()
        self.update()
        
        # New explosion?
        if time.time() - self._starttime > 1.0:
            self._new_explosion()
    
    
    def _new_explosion(self):
        
        # New centerpos
        centerpos = np.random.uniform(-0.5, 0.5, (3,))
        self._program.uniforms['u_centerPosition'] = centerpos
        
        # New color, scale alpha with N
        alpha = 1.0 / N**0.08
        color = np.random.uniform(0.1, 0.9, (3,))
        
        self._program.uniforms['u_color'] = tuple(color)+ (alpha,)
        
        # Create new vertex data
        vertex_data['a_lifetime'] = np.random.normal(1.0, 0.5, (N,))
        vertex_data['a_startPosition'] = np.random.normal(0.0, 0.2, (N,3))
        vertex_data['a_endPosition'] = np.random.normal(0.0, 1.2, (N,3))
       
        # Update VBO
        self._vbo.set_data(vertex_data)
        
        # Set time to zero
        self._starttime = time.time()


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
