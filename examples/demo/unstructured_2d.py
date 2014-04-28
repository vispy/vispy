# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author:   Per Rosengren
# Date:     18/03/2014
# Abstract: Unstructured2D canvas example
# Keywords: unstructured delaunay colormap
# Require: scipy
# ----------------------------------------------------------------------------
"""Unstructured2D canvas example.

Takes unstructured 2D locations, with corresponding 1 or 2 dimensional
scalar "values". Plots the values looked up from colormaps and
interpolated between the locations.
"""

import numpy as np
from vispy import gloo
from vispy import app
from vispy.gloo import gl
from vispy.util.transforms import ortho

import scipy.spatial


class Unstructured2d(app.Canvas):

    def __init__(self,
                 x=None, y=None, u=None, v=None,
                 colormap=None, data_lim=None,
                 dir_x_right=True, dir_y_top=True,
                 **kwargs):
        app.Canvas.__init__(self, close_keys=['escape'], **kwargs)
        self.create_shader(colormap)
        self.create_mesh(x, y, u, v)
        self.program.bind(self.vbo)
        if data_lim is not None:
            self._data_lim = data_lim
        else:
            self._data_lim = [[x.min(), x.max()], [y.min(), y.max()]]
        self._dir_x_right = dir_x_right
        self._dir_y_top = dir_y_top

    def create_shader(self, colormap):
        if len(colormap.shape) == 2:
            args = dict(
                n_dims="1",
                tex_t="float",
                texture2D_arg="vec2(v_texcoord, 0.)")
        else:
            args = dict(
                n_dims="2",
                tex_t="vec2",
                texture2D_arg="v_texcoord")
        vertex = """
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;
            uniform sampler2D texture;
            
            attribute vec2 position;
            attribute {tex_t} texcoord;
            
            varying {tex_t} v_texcoord;
            void main()
            {{
                gl_Position = projection * vec4(position, 0.0, 1.0);
                v_texcoord = texcoord;
            }}
        """.format(**args)

        fragment = """
            uniform sampler2D texture;
            varying {tex_t} v_texcoord;
            void main()
            {{
                gl_FragColor = texture2D(texture, {texture2D_arg});
            }}
        """.format(**args)

        self.program = gloo.Program(vertex, fragment)
        if len(colormap.shape) == 2:
            self.program['texture'] = colormap[None, :, :]
        else:
            self.program['texture'] = colormap
        self.program['texture'].interpolation = gl.GL_LINEAR
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)
        self.program['model'] = self.model
        self.program['view'] = self.view

    def create_mesh(self, x, y, u, v):
        tri = scipy.spatial.Delaunay(np.column_stack([x, y]))
        edges = tri.simplices.astype(np.uint32)
        uv = []
        for c in [u, v]:
            if c is not None:
                c = c.astype('f4')
                c = .5 + .5 * c / np.abs(c).max()
                uv.append(c)
        data = np.column_stack(
            [
                x.astype('f4'),
                y.astype('f4')
            ] + uv
        ).view(dtype=[('position', 'f4', 2),
                      ('texcoord', 'f4', 2 if v is not None else 1),
                      ])
        self.vbo = gloo.VertexBuffer(data)
        self.index = gloo.IndexBuffer(edges)

    def on_initialize(self, event):
        gl.glClearColor(1, 1, 1, 1)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.program.draw(gl.GL_TRIANGLES, self.index)

    def on_resize(self, event):
        self.resize(*event.size)

    def resize(self, width, height):
        gl.glViewport(0, 0, width, height)
        data_width = self._data_lim[0][1] - self._data_lim[0][0]
        data_height = self._data_lim[1][1] - self._data_lim[1][0]
        data_aspect = data_width / float(data_height)
        frame_aspect = width / float(height)
        if frame_aspect >= data_aspect:
            padding = (frame_aspect * data_height - data_width) / 2.
            frame_lim = [
                [self._data_lim[0][0] - padding,
                 self._data_lim[0][1] + padding],
                [self._data_lim[1][0],
                 self._data_lim[1][1]]]
        else:
            padding = (data_width / frame_aspect - data_height) / 2.
            frame_lim = [
                [self._data_lim[0][0],
                 self._data_lim[0][1]],
                [self._data_lim[1][0] - padding,
                 self._data_lim[1][1] + padding]]
        args_ortho = frame_lim[0][::(1 if self._dir_x_right else -1)]
        args_ortho += frame_lim[1][::(1 if self._dir_y_top else -1)]
        args_ortho += -1000, 1000
        self.program['projection'] = ortho(*args_ortho)


def create_colormap2d_hsv(size=512):
    import matplotlib.colors
    import math
    u, v = np.meshgrid(np.linspace(-1, 1, size), np.linspace(-1, 1, size))
    hsv = np.ones((size, size, 3), dtype=np.float32)
    hsv[:, :, 0] = (np.arctan2(u, v) / (2 * math.pi) + .5)
    hsv[:, :, 1] = np.minimum(1., np.sqrt(u ** 2 + v ** 2))
    rgb = matplotlib.colors.hsv_to_rgb(hsv)
    return rgb


def create_colormap2d_4dirs(size=512):
    rgb = np.ones((size, size, 3), dtype=np.float32)
    hs = size / 2
    u, v = np.meshgrid(np.linspace(1, 0, hs), np.linspace(1, 0, hs))
    rgb[:hs, :hs, 0] = 1.
    rgb[:hs, :hs, 1] = 1. - v + u / 2.
    rgb[:hs, :hs, 2] = 1. - np.maximum(u, v)
    u = u[:, ::-1]
    rgb[:hs, hs:, 0] = 1. - u + v
    rgb[:hs, hs:, 1] = 1. - np.maximum(u, v)
    rgb[:hs, hs:, 2] = 1. - v + u
    v = v[::-1, :]
    rgb[hs:, hs:, 0] = 1. - np.maximum(u, v)
    rgb[hs:, hs:, 1] = 1. - u + v
    rgb[hs:, hs:, 2] = 1. - v + u
    u = u[:, ::-1]
    rgb[hs:, :hs, 0] = 1. - v + u / 2.
    rgb[hs:, :hs, 1] = 1.
    rgb[hs:, :hs, 2] = 1. - np.maximum(u, v)
    rgb = np.minimum(1., rgb)
    return rgb


def create_colormap1d_hot(size=512):
    rgb = np.ones((size, 3), dtype=np.float32)
    hs = size / 2
    u = np.linspace(1, 0, hs)
    rgb[:hs, 0] = 1 - u
    rgb[:hs, 1] = 1 - u
    u = u[::-1]
    rgb[hs:, 1] = 1 - u
    rgb[hs:, 2] = 1 - u
    return rgb

if __name__ == '__main__':
    loc = np.random.random_sample(size=(100, 2))
    np.random.shuffle(loc)
    vec = np.empty_like(loc)
    vec[:, 0] = np.cos(loc[:, 0] * 10)
    vec[:, 1] = np.cos(loc[:, 1] * 13)
    width = 500
    height = 500
    c1 = Unstructured2d(title="Unstructured 2D - 2D colormap",
                        size=(width, height), position=(0, 0),
                        x=loc[:, 0], y=loc[:, 1], u=vec[:, 0], v=vec[:, 1],
                        colormap=create_colormap2d_4dirs(size=128))
    c2 = Unstructured2d(title="Unstructured 2D - 1D colormap",
                        size=(width, height), position=(width + 20, 0),
                        x=loc[:, 0], y=loc[:, 1], u=vec[:, 0],
                        colormap=create_colormap1d_hot(size=128))
    c1.show()
    c2.show()
    app.run()
