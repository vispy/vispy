# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from . import gl

GL_VERTEX_PROGRAM_POINT_SIZE = 34370
GL_POINT_SPRITE = 34913


def gl_initialize():
    """Initialize GL values

    This method helps standardize GL across desktop and mobile, e.g.
    by enabling ``GL_VERTEX_PROGRAM_POINT_SIZE`` and ``GL_POINT_SPRITE``.
    """
    gl.glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
    gl.glEnable(GL_POINT_SPRITE)
