# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Nicolas P .Rougier
# Date:   04/03/2014
# -----------------------------------------------------------------------------
"""
Show a rotating cube with lighting
==================================
"""

import numpy as np

from vispy import gloo, app
from vispy.gloo import Program, VertexBuffer, IndexBuffer
from vispy.util.transforms import perspective, translate, rotate
from vispy.geometry import create_cube


vertex = """
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform vec4 u_color;

attribute vec3 position;
attribute vec2 texcoord;
attribute vec3 normal;
attribute vec4 color;

varying vec3 v_position;
varying vec3 v_normal;
varying vec4 v_color;

void main()
{
    v_normal = normal;
    v_position = position;
    v_color = color * u_color;
    gl_Position = u_projection * u_view * u_model * vec4(position,1.0);
}
"""

fragment = """
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_normal;

uniform vec3 u_light_intensity;
uniform vec3 u_light_position;

varying vec3 v_position;
varying vec3 v_normal;
varying vec4 v_color;

void main()
{
    // Calculate normal in world coordinates
    vec3 normal = normalize(u_normal * vec4(v_normal,1.0)).xyz;

    // Calculate the location of this fragment (pixel) in world coordinates
    vec3 position = vec3(u_view*u_model * vec4(v_position, 1));

    // Calculate the vector from this pixels surface to the light source
    vec3 surfaceToLight = u_light_position - position;

    // Calculate the cosine of the angle of incidence (brightness)
    float brightness = dot(normal, surfaceToLight) /
                      (length(surfaceToLight) * length(normal));
    brightness = max(min(brightness,1.0),0.0);

    // Calculate final color of the pixel, based on:
    // 1. The angle of incidence: brightness
    // 2. The color/intensities of the light: light.intensities
    // 3. The texture and texture coord: texture(tex, fragTexCoord)

    gl_FragColor = v_color * brightness * vec4(u_light_intensity, 1);
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(512, 512), title='Lighted cube',
                            keys='interactive')
        self.timer = app.Timer('auto', self.on_timer)

        # Build cube data
        V, F, outline = create_cube()
        vertices = VertexBuffer(V)
        self.faces = IndexBuffer(F)
        self.outline = IndexBuffer(outline)

        # Build view, model, projection & normal
        # --------------------------------------
        self.view = translate((0, 0, -5))
        model = np.eye(4, dtype=np.float32)
        normal = np.array(np.matrix(np.dot(self.view, model)).I.T)

        # Build program
        # --------------------------------------
        self.program = Program(vertex, fragment)
        self.program.bind(vertices)
        self.program["u_light_position"] = 2, 2, 2
        self.program["u_light_intensity"] = 1, 1, 1
        self.program["u_model"] = model
        self.program["u_view"] = self.view
        self.program["u_normal"] = normal
        self.phi, self.theta = 0, 0

        self.activate_zoom()

        # OpenGL initialization
        # --------------------------------------
        gloo.set_state(clear_color=(0.30, 0.30, 0.35, 1.00), depth_test=True,
                       polygon_offset=(1, 1),
                       blend_func=('src_alpha', 'one_minus_src_alpha'),
                       line_width=0.75)
        self.timer.start()

        self.show()

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        # program.draw(gl.GL_TRIANGLES, indices)

        # Filled cube
        gloo.set_state(blend=False, depth_test=True, polygon_offset_fill=True)
        self.program['u_color'] = 1, 1, 1, 1
        self.program.draw('triangles', self.faces)

        # Outlined cube
        gloo.set_state(polygon_offset_fill=False, blend=True, depth_mask=False)
        self.program['u_color'] = 0, 0, 0, 1
        self.program.draw('lines', self.outline)
        gloo.set_state(depth_mask=True)

    def on_resize(self, event):
        self.activate_zoom()

    def activate_zoom(self):
        gloo.set_viewport(0, 0, *self.physical_size)
        projection = perspective(45.0, self.size[0] / float(self.size[1]),
                                 2.0, 10.0)
        self.program['u_projection'] = projection

    def on_timer(self, event):
        self.theta += .5
        self.phi += .5
        model = np.dot(rotate(self.theta, (0, 0, 1)),
                       rotate(self.phi, (0, 1, 0)))
        normal = np.linalg.inv(np.dot(self.view, model)).T
        self.program['u_model'] = model
        self.program['u_normal'] = normal
        self.update()

if __name__ == '__main__':
    c = Canvas()
    app.run()
