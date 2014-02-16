#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 60

"""
Points revolving around circles (revolving in a circle) to create a torus.
"""

import numpy as np
from vispy import gloo
from vispy import app
from vispy.gloo import gl
from vispy.util.transforms import perspective, translate, rotate


# points and offsets
n, p = 60, 15
do = 2 * np.pi / 600.
dt = -2 * np.pi / 900.
theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
omega = np.linspace(0, 2 * np.pi, p, endpoint=False)
theta = np.tile(theta[:, np.newaxis], (1, p)).ravel()
omega = np.tile(omega[np.newaxis, :], (n, 1)).ravel()

# colors (offset by one in adjacent "columns" of the torus)
ref = 0.6
dc = 2 * np.pi / 6
color = np.linspace(0, 2 * np.pi, p, endpoint=False)
color = np.array([(1-ref) * np.sin(color) + ref,
                  (1-ref) * np.sin(color + dc) + ref,
                  (1-ref) * np.sin(color + 2 * dc) + ref,
                  np.ones(color.shape)], dtype=np.float32).T
idx = np.arange(n * (p + 1)) % p
idx = np.reshape(idx, (n, p + 1))[:, :-1].ravel()
color = color[idx, :]
u_size = 10
u_amt = 0.25

data = np.zeros(n * p, [('a_omega', np.float32, 1),
                        ('a_theta', np.float32, 1),
                        ('a_color', np.float32, 4)])
data['a_color'] = color
data['a_omega'] = omega
data['a_theta'] = theta

VERT_SHADER = """
// Uniforms
// --------
uniform mat4  u_model;
uniform mat4  u_view;
uniform mat4  u_projection;
uniform float u_size;
uniform float u_amt;

// Attributes
// ----------
attribute float a_omega;
attribute float a_theta;
attribute vec4  a_color;
attribute mat4  a_model;

// Varyings
// --------
varying vec4 v_color;

void main (void) {
    v_color = a_color;
    float radius = (1 - u_amt) + (u_amt * cos(a_omega));
    float x = radius * cos(a_theta);
    float y = radius * sin(a_theta);
    float z = u_amt * sin(a_omega);
    gl_Position = u_projection * u_view * u_model
        * vec4(x, y, z, 1.0);
    gl_PointSize = u_size;
}
"""

FRAG_SHADER = """
// Varyings
// ------------------------------------
varying vec4 v_color;

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
        rotate(self.model, -60, 1, 0, 0)
        self.projection = np.eye(4, dtype=np.float32)
        self.translate = 3.5
        translate(self.view, 0, 0, -self.translate)

        self.vbo = gloo.VertexBuffer(data)
        self.program.set_vars(self.vbo)
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.program['u_size'] = u_size
        self.program['u_amt'] = u_amt

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
        self.update()

    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
        self.projection = perspective(45.0, width / float(height), 1.0, 1000.0)
        self.program['u_projection'] = self.projection

    def on_mouse_wheel(self, event):
        self.translate += event.delta[1]
        self.translate = min(max(2, self.translate), 10)
        self.view = np.eye(4, dtype=np.float32)
        translate(self.view, 0, 0, -self.translate)
        self.program['u_view'] = self.view
        self.update()

    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # update angles
        data['a_omega'] += do
        data['a_theta'] += dt
        # prevent accumulation
        data['a_omega'] %= 2 * np.pi
        data['a_theta'] %= 2 * np.pi
        self.vbo.set_data(data)
        self.program.draw(gl.GL_POINTS)


if __name__ == '__main__':
    c = Canvas(show=True, size=(600, 600),
               title="Atom [zoom with mouse scroll]")
    # c.show()
    app.run()
