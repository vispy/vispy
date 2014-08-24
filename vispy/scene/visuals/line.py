# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple visual based on GL_LINE_STRIP / GL_LINES


API issues to work out:

  * Currently this only uses GL_LINE_STRIP. Should add a 'method' argument like
    Image.method that can be used to select higher-quality triangle
    methods.

  * Add a few different position input components:
        - X values from vertex buffer of index values, Xmin, and Xstep
        - position from float texture

"""

from __future__ import division

import numpy as np

from ...color import Color
from ...gloo import set_state, VertexBuffer
from ..shaders import ModularProgram
from .visual import Visual


class Line(Visual):
    VERTEX_SHADER = """
        attribute vec2 a_position;

        void main(void)
        {
            gl_Position = $transform(vec4(a_position, 0., 1.0));
        }
    """

    FRAGMENT_SHADER = """
        uniform vec4 u_color;
        void main()
        {
            gl_FragColor = u_color;
        }
    """

    def __init__(self, pos=None, color=None, **kwargs):
        self._program = ModularProgram(self.VERTEX_SHADER,
                                       self.FRAGMENT_SHADER)
        self.set_data(pos=pos, color=color)
        Visual.__init__(self, **kwargs)

    def set_data(self, pos=None, color=None):
        self._vbo = VertexBuffer(np.asarray(pos, dtype=np.float32))
        self._color = Color(color).rgba

    def draw(self, event=None):
        if event is not None:
            xform = event.render_transform.shader_map()
            self._program.vert['transform'] = xform
        self._program.prepare()
        self._program['a_position'] = self._vbo
        self._program['u_color'] = self._color
        set_state(blend=True, blend_func=('src_alpha', 'one_minus_src_alpha'))
        self._program.draw('line_strip')


