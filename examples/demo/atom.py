#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 60

"""
Particles orbiting around a central point (with traces)
"""

import numpy as np
from vispy import gloo
from vispy import app
from vispy.gloo import gl
from vispy.util.transforms import perspective, translate, rotate


n, p = 250, 50
T = np.random.uniform(0, 2 * np.pi, n)
dT = np.random.uniform(50, 100, n) / 3000
position = np.zeros((n, 2), dtype=np.float32)
position[:, 0] = np.cos(T)
position[:, 1] = np.sin(T)
rot = np.random.uniform(0, 2 * np.pi, (n, 4)).astype(np.float32)
color = np.ones((n, 4), dtype=np.float32) * (1, 1, 1, 1)
u_size = 6

data = np.zeros(n * p, [('a_position', np.float32, 2),
                        ('a_color', np.float32, 4),
                        ('a_rot', np.float32, 4)])
data['a_position'] = np.repeat(position, p, axis=0)
data['a_color'] = np.repeat(color, p, axis=0)
data['a_rot'] = np.repeat(rot, p, axis=0)


VERT_SHADER = """
// Uniforms
// --------
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_size;

// Attributes
// ----------
attribute vec2  a_position;
attribute vec4  a_rot;
attribute vec4  a_color;
attribute mat4  a_model;

// Varyings
// --------
varying vec4 v_color;
varying float v_size;

mat4 rotation(vec3 axis, float angle) {
    axis = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float oc = 1.0 - c;
    return mat4(oc * axis.x * axis.x + c,
                oc * axis.x * axis.y - axis.z * s,
                oc * axis.z * axis.x + axis.y * s,
                0.0,
                oc * axis.x * axis.y + axis.z * s,
                oc * axis.y * axis.y + c,
                oc * axis.y * axis.z - axis.x * s,
                0.0,
                oc * axis.z * axis.x - axis.y * s,
                oc * axis.y * axis.z + axis.x * s,
                oc * axis.z * axis.z + c,
                0.0,
                0.0, 0.0, 0.0, 1.0);
}

void main (void) {
    v_size = u_size;
    v_color = a_color;

    mat4 R = rotation(a_rot.xyz, a_rot.w);
    gl_Position = u_projection * u_view * u_model * R
        * vec4(a_position, 0.0, 1.0);
    gl_PointSize = v_size;
}
"""

FRAG_SHADER = """

// Varyings
// ------------------------------------
varying vec4 v_color;
varying float v_size;

// Main
// ------------------------------------
void main()
{
    float d = 2*(length(gl_PointCoord.xy - vec2(0.5,0.5)));
    gl_FragColor = vec4(v_color.rgb, v_color.a*(1-d));
}
"""


class Canvas(app.Canvas):

    def __init__(self, **kwargs):

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)
        self.translate = 3
        translate(self.view, 0, 0, -self.translate)

        self.vbo = gloo.VertexBuffer(data)
        self.program.set_vars(self.vbo)
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.program['u_size'] = u_size

        self.theta = 0
        self.phi = 0
        self.index = 0

        self.timer = app.Timer(1.0 / 400)
        self.timer.connect(self.on_timer)
        self.timer.start()

        # Initialize the canvas for real
        app.Canvas.__init__(self, **kwargs)

    def on_initialize(self, event):
        gl.glClearColor(0, 0, 0, 1)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def on_key_press(self, event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()

    def on_timer(self, event):
        self.theta += .017
        self.phi += .013
        self.model = np.eye(4, dtype=np.float32)
        rotate(self.model, self.theta, 0, 0, 1)
        rotate(self.model, self.phi, 0, 1, 0)
        self.program['u_model'] = self.model
        self.update()

    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
        self.projection = perspective(45.0, width / float(height), 1.0, 1000.0)
        self.program['u_projection'] = self.projection

    def on_mouse_wheel(self, event):
        global u_size

        self.translate += event.delta[1]
        self.translate = max(2, self.translate)
        self.view = np.eye(4, dtype=np.float32)
        translate(self.view, 0, 0, -self.translate)
        self.program['u_view'] = self.view
        self.update()

    def on_paint(self, event):
        global T, dT, p, n
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        T += dT
        self.index = (self.index + 1) % p
        data['a_position'][self.index::p, 0] = np.cos(T)
        data['a_position'][self.index::p, 1] = .5 * np.sin(T)
        data['a_color'][:, 3] -= 1.0 / p
        data['a_color'][self.index::p, 3] = 1
        self.vbo.set_data(data)
        self.program.draw(gl.GL_POINTS)


if __name__ == '__main__':
    c = Canvas(
        show=True,
        size=(
            600,
            600),
        title="Atom [zoom with mouse scroll]")
    # c.show()
    app.run()
