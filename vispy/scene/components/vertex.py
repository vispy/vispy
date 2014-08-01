# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Vertex components are modular shader components used for retrieving or
generating untransformed vertex locations.

These components create a function in the vertex shader that accepts no
arguments and returns a vec4 vertex location in the local coordinate system
of the visual.
"""

from __future__ import division

import numpy as np

from .component import VisualComponent
from ... import gloo


class XYPosComponent(VisualComponent):
    """
    generate local coordinate from xy (vec2) attribute and z (float) uniform
    """
    SHADERS = dict(
        local_position="""
            vec4 input_xy_pos() {
                return vec4($xy_pos, $z_pos, 1.0);
            }
        """)

    def __init__(self, xy=None, z=0.0, index=None):
        super(XYPosComponent, self).__init__()
        self._xy = None
        self._z = 0.0
        self._index = False
        self._vbo = None
        self._ibo = None
        self.set_data(xy[:, :2], z, index)

    @property
    def supported_draw_modes(self):
        # TODO: Add support for converting between pre-indexed and unindexed
        if self._index is False:
            return set([self.DRAW_PRE_INDEXED])
        else:
            return set([self.DRAW_UNINDEXED])

    def set_data(self, xy=None, z=None, index=None):
        if xy is not None:
            self._xy = xy
        if z is not None:
            self._z = z
        if index is not None:
            self._index = index
        # TODO: might be better to re-upload data rather than creating
        # a new VB, if possible.
        self._vbo = None
        self.update()

    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self._xy)
        return self._vbo

    @property
    def ibo(self):
        if self._ibo is None:
            self._ibo = gloo.IndexBuffer(self._index)
        return self._ibo

    def activate(self, program, draw_mode):
        fn = self._funcs['local_position']
        #fn['xy_pos'] = ('attribute', 'vec2', self.vbo)
        #fn['z_pos'] = ('uniform', 'float', self._z)
        fn['xy_pos'] = self.vbo
        fn['z_pos'] = self._z

    @property
    def index(self):
        if self._index is False:
            return None
        else:
            return self.ibo


class XYZPosComponent(VisualComponent):
    """
    generate local coordinate from xyz (vec3) attribute
    """
    SHADERS = dict(
        local_position="""
            vec4 input_xyz_pos() {
                return vec4($xyz_pos, 1.0);
            }
        """)

    def __init__(self, pos=None, index=None):
        super(XYZPosComponent, self).__init__()
        self._pos = None
        self._index = False
        self._vbo = None
        self._ibo = None
        self.set_data(pos, index)

    @property
    def supported_draw_modes(self):
        # TODO: Add support for converting between pre-indexed and unindexed
        if self._index is False:
            return set([self.DRAW_PRE_INDEXED])
        else:
            return set([self.DRAW_UNINDEXED])

    def set_data(self, pos=None, index=None):
        if pos is not None:
            self._pos = pos
        if index is not None:
            self._index = index
        # TODO: might be better to re-upload data rather than creating
        # a new VB, if possible.
        self._vbo = None
        self.update()

    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self._pos)
        return self._vbo

    @property
    def ibo(self):
        if self._ibo is None:
            self._ibo = gloo.IndexBuffer(self._index)
        return self._ibo

    def activate(self, program, draw_mode):
        #self._funcs['local_position']['xyz_pos'] = ('attribute', 'vec3',
                                                    #self.vbo)
        self._funcs['local_position']['xyz_pos'] = self.vbo

    @property
    def index(self):
        if self._index is False:
            return None
        else:
            return self.ibo


class HeightFieldComponent(VisualComponent):
    """
    Generate vertex coordinate from 2D array of z-positions.

    x,y will be generated in the vertex shader using uniforms that specify the
    range.
    """
    SHADERS = dict(
        local_position="""
            vec4 input_z_pos() {
                int xind = int($index % $x_size);
                float x = $x_min + (xind * $x_step);
                int yind = int($index % $y_size);
                float y = $y_min + (yind * $y_step);
                return vec4(x, y, $z_pos, 1.0);
            }
        """)

    def __init__(self, z=None):
        super(HeightFieldComponent, self).__init__()
        self._z = None
        self._vbo = None
        if z is not None:
            self.set_data(z)

    @property
    def supported_draw_modes(self):
        # TODO: add support for pre-indexed data
        # (possibly here, possibly in another component class?)
        return set([self.DRAW_UNINDEXED])

    def set_data(self, z):
        if self._z is None or self._z.shape != z.shape:
            # if this data has a new shape, we need a new index buffer
            self._ibo = None

        self._z = z
        # TODO: might be better to re-upload data rather than creating
        # a new VB, if possible.
        self._vbo = None

        self.update()

    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self._z)
            self._index = gloo.VertexBuffer(np.arange(self._z.size))
        return self._vbo

    def activate(self, program, draw_mode):
        self._funcs['local_position']['z_pos'] = self.vbo  # attribute vec3

    @property
    def index(self):
        """
        The IndexBuffer used by this input component.
        """
        if self._ibo is None:
            cols = self._z.shape[1]-1
            rows = self._z.shape[0]-1
            faces = np.empty((cols*rows*2, 3), dtype=np.uint)
            rowtemplate1 = (np.arange(cols).reshape(cols, 1) +
                            np.array([[0, 1, cols+1]]))
            rowtemplate2 = (np.arange(cols).reshape(cols, 1) +
                            np.array([[cols+1, 1, cols+2]]))
            for row in range(rows):
                start = row * cols * 2
                faces[start:start+cols] = rowtemplate1 + row * (cols+1)
                faces[start+cols:start+(cols*2)] = (rowtemplate2 +
                                                    row * (cols+1))
            self._ibo = gloo.IndexBuffer(faces)
        return self._ibo
