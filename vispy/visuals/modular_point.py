# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ... import gloo
from .modular_visual import ModularVisual
from ..shaders import Function


class ModularPoint(ModularVisual):
    """
    Displays multiple point sprites.
    """
    def __init__(self, pos=None, color=None, **kwargs):
        super(ModularPoint, self).__init__(**kwargs)

        glopts = kwargs.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)

        if pos is not None or color is not None:
            self.set_data(pos=pos, color=color)

        # TODO: turn this into a proper component.
        code = """
        void set_point_size() {
            gl_PointSize = 10.0; //size;
        }
        """
        self._program.vert.add_callback('vert_post_hook', Function(code))

    @property
    def primitive(self):
        return gloo.gl.GL_POINTS

    def draw(self, event):
        # HACK: True OpenGL ES does not need to enable point sprite and does
        # not define these two constants. Desktop OpenGL needs to enable these
        # two modes but we do not have these two constants because our GL
        # namespace pretends to be ES.
        GL_VERTEX_PROGRAM_POINT_SIZE = 34370
        GL_POINT_SPRITE = 34913
        gloo.gl.glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
        gloo.gl.glEnable(GL_POINT_SPRITE)
        super(ModularPoint, self).draw(event)
