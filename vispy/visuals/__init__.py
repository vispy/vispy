# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Subpackage that defines a collection of visuals. A visual implements
a raw version of a visualization based on OpenGL. There is no
scene graph or transforms.

Nevertheless, the GLSL code of the visuals will have some code for
transforms, lighting etc. Later we will probably use shader chaining
and we would only need some hooks in GLSL of the visuals.
"""

from __future__ import division

from .. import gloo


class BaseVisual(object):

    """ Abstract visual class.
    """

    VERT_SHADER = ""
    FRAG_SHADER = ""
    MODE = "POINTS"

    def __init__(self):
        # Create program
        self._program = gloo.Program(self.VERT_SHADER, self.FRAG_SHADER)

    @property
    def program(self):
        """ The shader program (a gloo.Program object) for this visual.
        """
        return self._program

    def draw(self):
        """ draw this visual.
        """
        self.program.draw(self.MODE)


# Import visuals in this namespace
from .points import PointsVisual  # noqa
