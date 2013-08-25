# #!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from vispy import oogl
from vispy import app
from vispy import gl
from OpenGL import GL
import numpy as np

# Create vetices 
n = 100
a_position = np.random.uniform(-1,1,(n,2))
a_id = np.random.randint(0,20,(n,1))
a_id = np.sort(a_id,axis=0)

print a_id


from transforms import perspective, translate, rotate


VERT_SHADER = """
#version 120

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

attribute vec3  a_position;
attribute float a_id;

varying float v_id;

void main (void) {
    v_id = a_id;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
}
"""

FRAG_SHADER = """
#version 120
varying float v_id;
void main()
{    
    if((v_id - floor(v_id) > 0))
        discard;

    gl_FragColor = vec4(0,0,0,1);
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
        self.program.attributes['a_id'] = a_id
        self.program.attributes['a_position'] = a_position

        self.view       = np.eye(4,dtype=np.float32)
        self.model      = np.eye(4,dtype=np.float32)
        self.projection = np.eye(4,dtype=np.float32)

        self.translate = 5
        translate(self.view, 0,0, -self.translate)
        self.program.uniforms['u_model'] = self.model
        self.program.uniforms['u_view'] = self.view

        self.theta = 0
        self.phi = 0

        self.timer = app.Timer(1.0/60)
        self.timer.connect(self.on_timer)
        #self.timer.start()


    # ---------------------------------
    def on_initialize(self, event):
        gl.glClearColor(1,1,1,1)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(GL.GL_POINT_SPRITE)


    # ---------------------------------
    def on_key_press(self,event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()


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
        self.projection = perspective( 45.0, width/float(height), 1.0, 1000.0 )
        self.program.uniforms['u_projection'] = self.projection


    # ---------------------------------
    def on_mouse_wheel(self, event):
        self.translate +=event.delta[1]
        self.translate = max(2,self.translate)
        self.view       = np.eye(4,dtype=np.float32)
        translate(self.view, 0,0, -self.translate)
        self.program.uniforms['u_view'] = self.view
        self.program.attributes['a_size'] = a_size*5/self.translate
        self.update()


    # ---------------------------------
    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        with self.program as prog:
            prog.draw_arrays(gl.GL_LINE_STRIP)


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
