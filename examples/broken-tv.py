# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

""" 
Example demonstrating showing a quad. Like hello_quad1.py, but now
with Texture2D and VertexBuffer, and optionally using an ElementBuffer to
draw the vertices.
"""

import time
import numpy as np

from vispy import oogl
from vispy import app
from vispy import gl


data = np.zeros(4, dtype=[   ('a_position', np.float32, 3), 
                             ('a_texcoord', np.float32, 2) ])
data['a_position'] = np.array([ [-1, -1, 0], [1, -1, 0],  
                                [-1,  1, 0], [1,  1, 0] ])
data['a_texcoord'] = np.array([ [0, 0], [0, 1], [1, 0], [1, 1] ])


VERT_SHADER = """
attribute vec3 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;
void main (void) {
    v_texcoord = a_texcoord;
    gl_Position = vec4(a_position,1);
}
"""

FRAG_SHADER = """
uniform sampler2D u_texture;
varying vec2 v_texcoord;
void main()
{    
    gl_FragColor = texture2D(u_texture, v_texcoord);
    gl_FragColor.a = 1.0;
}

"""


class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)
        
        self._program = oogl.ShaderProgram( oogl.VertexShader(VERT_SHADER), 
                                            oogl.FragmentShader(FRAG_SHADER) )
        self._vbo = oogl.VertexBuffer(data)

        im = np.random.uniform(0,1,(256,256)).astype(np.float32)
        self._texture = oogl.Texture2D(im)

        self._program.uniforms['u_texture'] = self._texture
        self._program.attributes['a_position'] = self._vbo['a_position']
        self._program.attributes['a_texcoord'] = self._vbo['a_texcoord']
        
    
    def on_initialize(self, event):
        gl.glClearColor(1,1,1,1)
    
    
    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
    
    
    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        with self._program as prog:
            im = np.random.uniform(0,1,(256,256)).astype('float32')
            self._texture.set_data(im)
            prog.draw_arrays(gl.GL_TRIANGLE_STRIP)
        self.update()


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
