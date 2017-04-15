# !/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# 2014, Aurore Deschildre, Gael Goret, Cyrille Rossant, Nicolas P. Rougier.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import numpy as np

import OpenGL.GL as gl

from vispy import gloo
from vispy import app
from vispy.util.transforms import perspective, translate, rotate

vertex = """
#version 120

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform vec3 u_light_position;
uniform vec3 u_light_spec_position;

attribute vec3  a_position;
attribute vec3  a_color;
attribute float a_radius;

varying vec3  v_color;
varying vec4  v_eye_position;
varying float v_radius;
varying vec3  v_light_direction;

void main (void) {
    v_radius = a_radius;
    v_color = a_color;

    v_eye_position = u_view * u_model * vec4(a_position,1.0);
    v_light_direction = normalize(u_light_position);
    float dist = length(v_eye_position.xyz);

    gl_Position = u_projection * v_eye_position;

    // stackoverflow.com/questions/8608844/...
    //  ... resizing-point-sprites-based-on-distance-from-the-camera
    vec4  proj_corner = u_projection * vec4(a_radius, a_radius, v_eye_position.z, v_eye_position.w);
    gl_PointSize = 512.0 * proj_corner.x / proj_corner.w;
}
"""

fragment = """
#version 120

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform vec3 u_light_position;
uniform vec3 u_light_spec_position;

varying vec3  v_color;
varying vec4  v_eye_position;
varying float v_radius;
varying vec3  v_light_direction;
void main()
{
    // r^2 = (x - x0)^2 + (y - y0)^2 + (z - z0)^2
    vec2 texcoord = gl_PointCoord* 2.0 - vec2(1.0);
    float x = texcoord.x;
    float y = texcoord.y;
    float d = 1.0 - x*x - y*y;
    if (d <= 0.0)
        discard;

    float z = sqrt(d);
    vec4 pos = v_eye_position;
    pos.z += v_radius*z;
    vec3 pos2 = pos.xyz;
    pos = u_projection * pos;
    gl_FragDepth = 0.5*(pos.z / pos.w)+0.5;
    vec3 normal = vec3(x,y,z);
    float diffuse = clamp(dot(normal, v_light_direction), 0.0, 1.0);
    
    // Specular lighting.
    vec3 M = pos2.xyz;
    vec3 O = v_eye_position.xyz;
    vec3 L = u_light_spec_position;
    vec3 K = normalize(normalize(L - M) + normalize(O - M));
    // WARNING: abs() is necessary, otherwise weird bugs may appear with some
    // GPU drivers...
    float specular = clamp(pow(abs(dot(normal, K)), 40.), 0.0, 1.0);
    vec3 v_light = vec3(1., 1., 1.);
    gl_FragColor.rgb = .15*v_color +  .55*diffuse * v_color + .35*specular * v_light;
}
"""

class MolecularViewerCanvas(app.Canvas):

    def __init__(self, fname):
        app.Canvas.__init__(self, title = 'Molecular viewer')
        self.size = 1200, 800

        self.program = gloo.Program(vertex, fragment)
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)
        self.translate = 40
        translate(self.view, 0, 0, -self.translate)
        
        self.load_molecule(fname)
        self.load_data()

        self.theta = 0
        self.phi = 0

        self.timer = app.Timer(1.0 / 30)# change rendering speed here
        self.timer.connect(self.on_timer)
        self.timer.start()
        
    
    def load_molecule(self, fname):
        
        molecule = np.load(fname)        
        self._nAtoms = molecule.shape[0]
        
        # The x,y,z values store in one array
        self.coords = molecule[:,:3]

        # The array that will store the color and alpha scale for all the atoms.
        self.atomsColours = molecule[:,3:6]

        # The array that will store the scale for all the atoms. 
        self.atomsScales = molecule[:,6]

    
    def load_data(self):
        n = self._nAtoms
        
        data = np.zeros(n, [('a_position', np.float32, 3),
                            ('a_color', np.float32, 3),
                            ('a_radius', np.float32, 1)])
        
        data['a_position'] = self.coords
        data['a_color'] = self.atomsColours
        data['a_radius'] = self.atomsScales
        
        self.program.set_vars(gloo.VertexBuffer(data))
        
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.program['u_light_position'] = 0., 0., 2.
        self.program['u_light_spec_position'] = -5., 5., -5.
        

    def on_initialize(self, event):
        gl.glClearColor(0, 0, 0, 1)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(gl.GL_POINT_SPRITE)


    def on_key_press(self, event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()
        # if event.text == 'A':
            # self.


    def on_timer(self, event):
        self.theta += .5
        self.phi += .5
        self.model = np.eye(4, dtype=np.float32)
        
        rotate(self.model, self.theta, 0, 0, 1)
        rotate(self.model, self.phi, 0, 1, 0)
        
        self.program['u_model'] = self.model
        self.update()

    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
        self.projection = perspective( 25.0, width/float(height), 2.0, 100.0 )
        self.program['u_projection'] = self.projection

    def on_mouse_wheel(self, event):
        self.translate -= event.delta[1]
        self.translate = max(-1, self.translate)
        self.view = np.eye(4, dtype=np.float32)
        
        translate(self.view, 0, 0, -self.translate)

        self.program['u_view'] = self.view
        self.update()

    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.program.draw(gl.GL_POINTS)


def main(fname):
    mvc = MolecularViewerCanvas(fname)
    mvc.show()
    app.run()

if __name__ == '__main__':
    main('micelle.npy')
