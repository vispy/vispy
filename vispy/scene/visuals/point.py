# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from ... import gloo
from .visual import Visual
from ..components import (XYPosComponent, XYZPosComponent, 
                         UniformColorComponent, VertexColorComponent)
from ..shaders import Function

class Point(Visual):
    """
    Displays multiple point sprites.
    """
    def __init__(self, pos=None, **kwds):
        super(Point, self).__init__()
        
        glopts = kwds.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)
        
        if pos is not None or kwds:
            self.set_data(pos, **kwds)
            
        # TODO: turn this into a proper component.
        code = """
        void $set_point_size() {
            gl_PointSize = 10.0; //size;
        }
        """
        self._program.add_callback('vert_post_hook', Function(code))

    @property
    def primitive(self):
        return gloo.gl.GL_POINTS

    def paint(self):
        # HACK: True OpenGL ES does not need to enable point sprite and does not define
        # these two constants. Desktop OpenGL needs to enable these two modes but we do
        # not have these two constants because our GL namespace pretends to be ES.
        GL_VERTEX_PROGRAM_POINT_SIZE = 34370
        GL_POINT_SPRITE = 34913
        gloo.gl.glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
        gloo.gl.glEnable(GL_POINT_SPRITE)
        super(Point, self).paint()
