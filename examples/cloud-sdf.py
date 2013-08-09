# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

""" Simple example plotting 2D points.
"""

import os

from vispy import oogl
from vispy import app
from vispy import gl
from OpenGL import GL
import numpy as np

from transforms import perspective, translate, rotate

# Create vetices 
n = 10000
v_position = 0.5 * np.random.randn(n, 3).astype(np.float32)
v_color = np.random.uniform(0.50,1.00,(n,3)).astype(np.float32)
v_size  = np.random.uniform(10,20,(n,1)).astype(np.float32)

# Define marker image
marker_image = 'star-sdf.png'
# marker_image = 'clober-sdf.png'
# marker_image = 'cross-sdf.png'

# Get marker filename
THISDIR = os.path.dirname(os.path.abspath(__file__))
marker_filename = os.path.join(THISDIR, 'data', marker_image)


VERT_SHADER = """
#version 120

// Uniforms
// ------------------------------------
uniform   mat4 u_model;
uniform   mat4 u_view;
uniform   mat4 u_projection;
uniform   vec4 u_color;

// Attributes
// ------------------------------------
attribute vec3  a_position;
attribute vec3  a_color;
attribute float a_size;

// Varying
// ------------------------------------
varying float v_size;
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_linewidth;
varying float v_antialias;

void main (void) {
    v_linewidth = 1.5;
    v_antialias = 1.0;
    v_size = a_size;
    v_fg_color  = vec4(0.0,0.0,0.0,0.5);
    v_bg_color  = vec4(a_color,    1.0);
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
    gl_PointSize = 2.0*(a_size + v_linewidth + 1.5*v_antialias);
}
"""

FRAG_SHADER = """
#version 120

// Uniforms
// ------------------------------------
uniform   sampler2D u_texture;

// Varying
// ------------------------------------
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_linewidth;
varying float v_antialias;
varying float v_size;
void main()
{    
    float size = v_size; // - v_linewidth - 1.5*v_antialias);
    float t = v_linewidth/2.0-v_antialias;

    // SDF circle
    float r = size*texture2D(u_texture, gl_PointCoord.xy).a;
    float d = abs(r) - t;

    if( r > (v_linewidth/2.0+v_antialias))
        discard;

    if( d < 0.0 )
        gl_FragColor = v_fg_color;
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r >= 0.0)
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        else
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
    }
}
"""



class Canvas(app.Canvas):

    # ---------------------------------
    def __init__(self):
        app.Canvas.__init__(self)
        self.geometry = (0,0,1000,1000)

        self.program = oogl.ShaderProgram( oogl.VertexShader(VERT_SHADER), 
                                           oogl.FragmentShader(FRAG_SHADER) )
        # Set uniform and attribute
        self.program.attributes['a_color']    = v_color
        self.program.attributes['a_position'] = v_position
        self.program.attributes['a_size']     = v_size

        self.view       = np.eye(4,dtype=np.float32)
        self.model      = np.eye(4,dtype=np.float32)
        self.projection = np.eye(4,dtype=np.float32)

        translate(self.view, 0,0,-5)
        self.program.uniforms['u_model'] = self.model
        self.program.uniforms['u_view'] = self.view

        n = 256
        X,Y = np.meshgrid(np.linspace(-0.5,+0.5,n,endpoint=True),
                          np.linspace(-0.5,+0.5,n,endpoint=True))
        D = (np.sqrt(X*X+Y*Y) - 0.45).astype(np.float32)
        self.program.uniforms['u_texture'] = oogl.Texture2D(data=D, format=gl.GL_ALPHA)

        from PIL import Image
        im = Image.open(marker_filename)
        D = np.asarray(im)[:,:]
        D = (D/256.0 - 0.5).astype(np.float32)
        print(D.shape, D.min(), D.max())
        self.program.uniforms['u_texture'] = oogl.Texture2D(data=D, format=gl.GL_ALPHA)

        self.theta = 0
        self.phi = 0

        self._timer = app.Timer(1.0/60)
        self._timer.connect(self.on_timer)
        self._timer.start()


    # ---------------------------------
    def on_initialize(self, event):
        gl.glClearColor(1,1,1,1)
        gl.glEnable(gl.GL_DEPTH_TEST)


    # ---------------------------------
    def on_timer(self,event):
        self.theta += .5
        self.phi += .5
        self.model = np.eye(4, dtype=np.float32)
        rotate(self.model, self.theta, 0,0,1)
        rotate(self.model, self.phi,   0,1,0)
        self.program.uniforms['u_model'] = self.model
        self.update()


    # ---------------------------------
    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
        self.projection = perspective( 45.0, width/float(height), 2.0, 10.0 )
        self.program.uniforms['u_projection'] = self.projection


    # ---------------------------------
    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(GL.GL_POINT_SPRITE)
        with self.program as prog:
            prog.draw_arrays(gl.GL_POINTS)
        self.swap_buffers()

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
