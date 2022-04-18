# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demonstration of cube mapping with trackball interaction.
"""
import numpy as np
from math import cos, sin, pi
from vispy import app, gloo
from vispy.gloo import gl
from vispy.io import read_png, load_data_file
from vispy.util.transforms import perspective


def lookAt(eye, target, up=[0, 0, 1]):
    """Computes matrix to put eye looking at target point."""
    eye = np.asarray(eye).astype(np.float32)
    target = np.asarray(target).astype(np.float32)
    up = np.asarray(up).astype(np.float32)

    vforward = eye - target
    vforward /= np.linalg.norm(vforward)
    vright = np.cross(up, vforward)
    vright /= np.linalg.norm(vright)
    vup = np.cross(vforward, vright)

    view = np.r_[vright, -np.dot(vright, eye),
                 vup, -np.dot(vup, eye),
                 vforward, -np.dot(vforward, eye),
                 [0, 0, 0, 1]].reshape(4, 4, order='F')

    return view


def getView(azimuth, elevation, distance, target=[0, 0, 0]):
    """Computes view matrix based on angle, distance and target."""
    x = distance * sin(elevation) * sin(azimuth)
    y = distance * sin(-elevation) * cos(azimuth)
    z = distance * cos(elevation)
    return lookAt([x, y, z], target)


vertex_shader = """
attribute vec3 a_position;
attribute vec3 a_texcoord;
varying vec3 v_texcoord;
uniform   mat4 u_model;
uniform   mat4 u_view;
uniform   mat4 u_projection;

void main()
{
    v_texcoord = a_texcoord;
    gl_Position = u_projection * u_view * u_model * vec4(a_position, 1.0);
}
"""

fragment_shader = """
uniform samplerCube a_texture;
varying vec3 v_texcoord;

void main()
{
    gl_FragColor = textureCube(a_texture, v_texcoord);
}
"""

vertices = np.array([[+1, +1, +1], [-1, +1, +1], [-1, -1, +1], [+1, -1, +1],
                     [+1, -1, -1], [+1, +1, -1], [-1, +1, -1], [-1, -1, -1]]).astype(np.float32)
faces = np.array([vertices[i] for i in [0, 1, 2, 3, 0, 3, 4, 5, 0, 5, 6, 1,
                                        6, 7, 2, 1, 7, 4, 3, 2, 4, 7, 6, 5]])
indices = np.resize(np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32), 36)
indices += np.repeat(4 * np.arange(6, dtype=np.uint32), 6)

texture = np.zeros((6, 1024, 1024, 3), dtype=np.float32)
texture[2] = read_png(load_data_file("skybox/sky-left.png"))/255.
texture[3] = read_png(load_data_file("skybox/sky-right.png"))/255.
texture[0] = read_png(load_data_file("skybox/sky-front.png"))/255.
texture[1] = read_png(load_data_file("skybox/sky-back.png"))/255.
texture[4] = read_png(load_data_file("skybox/sky-up.png"))/255.
texture[5] = read_png(load_data_file("skybox/sky-down.png"))/255.


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, size=(1024, 1024), title='Skybox example',
                            keys='interactive')

        self.cubeSize = 10
        self.pressed = False
        self.azimuth = pi / 2.0
        self.elevation = pi / 2.0
        self.distanceMin = 1
        self.distanceMax = 50
        self.distance = 30
        self.sensitivity = 5.0
        self.view = getView(self.azimuth, self.elevation, self.distance)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.program = gloo.Program(vertex_shader, fragment_shader, count=24)
        self.program['a_position'] = faces*self.cubeSize
        self.program['a_texcoord'] = faces
        self.program['a_texture'] = gloo.TextureCube(texture, interpolation='linear')
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        gloo.set_viewport(0, 0, *self.physical_size)
        self.projection = perspective(60.0, self.size[0] /
                                      float(self.size[1]), 1.0, 100.0)
        self.program['u_projection'] = self.projection

        gl.glEnable(gl.GL_DEPTH_TEST)
        gloo.set_clear_color('black')
        self.show()

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw(gl.GL_TRIANGLES, gloo.IndexBuffer(indices))

    def on_mouse_wheel(self, event):
        self.distance = self.distance - event.delta[1]
        self.distance = min(max(self.distance, self.distanceMin), self.distanceMax)
        self.program['u_view'] = getView(self.azimuth, self.elevation, self.distance)
        self.update()

    def on_mouse_press(self, event):
        self.pressed = True
        self.mousex = event.pos[0]
        self.mousey = event.pos[1]

    def on_mouse_release(self, event):
        self.pressed = False

    def on_mouse_move(self, event):
        if self.pressed:
            dazimuth = (event.pos[0] - self.mousex) * (2*pi) / self.size[0]
            delevation = (event.pos[1] - self.mousey) * (2*pi) / self.size[1]
            self.mousex = event.pos[0]
            self.mousey = event.pos[1]
            self.azimuth = (self.azimuth - dazimuth/self.sensitivity)
            self.elevation = (self.elevation - delevation/self.sensitivity)
            self.program['u_view'] = getView(self.azimuth, self.elevation, self.distance)
            self.update()


if __name__ == '__main__':
    c = Canvas()
    app.run()
