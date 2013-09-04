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
n = 10000
v_position = 0.25 * np.random.randn(n, 2).astype(np.float32)
v_color = np.random.uniform(0,1,(n,3)).astype(np.float32)
v_size  = np.random.uniform(2,12,(n,1)).astype(np.float32)

VERT_SHADER = """
#version 120

attribute vec3  a_position;
attribute vec3  a_color;
attribute float a_size;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;
varying float v_linewidth;
varying float v_antialias;

void main (void) {
    v_radius = a_size;
    v_linewidth = 1.0;
    v_antialias = 1.0;
    v_fg_color  = vec4(0.0,0.0,0.0,0.5);
    v_bg_color  = vec4(a_color,    1.0);

    gl_Position = vec4(a_position, 1.0);
    gl_PointSize = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
}
"""

FRAG_SHADER = """
#version 120

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;
varying float v_linewidth;
varying float v_antialias;
void main()
{    
    float size = 2*(v_radius + v_linewidth + 1.5*v_antialias);
    float t = v_linewidth/2.0-v_antialias;
    float r = length((gl_PointCoord.xy - vec2(0.5,0.5))*size);
    float d = abs(r - v_radius) - t;
    if( d < 0.0 )
        gl_FragColor = v_fg_color;
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r > v_radius)
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        else
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
    }
}
"""



class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self)

        self.program = oogl.Program(VERT_SHADER, FRAG_SHADER)
        
        # Set uniform and attribute
        self.program['a_color']    = oogl.VertexBuffer(v_color)
        self.program['a_position'] = oogl.VertexBuffer(v_position)
        self.program['a_size']     = oogl.VertexBuffer(v_size)
    
    
    def on_initialize(self, event):
        gl.glClearColor(1,1,1,1)
        
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        # Enable point sprites (allow to change the size of the points with
        # gl_PointSize in the vertex shader)
        # NOTE: this should not be necessary in futere versions of vispy
        gl.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(GL.GL_POINT_SPRITE)
    
    
    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
    
    
    def on_paint(self, event):
        # Clear
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Draw
        with self.program as prog:
            prog.draw_arrays(gl.GL_POINTS)


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
