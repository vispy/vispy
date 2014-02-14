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


class Visual(object):

    """ Abstract visual class.
    """
    # TODO: As we write more visuals, we can decide on what common components 
    # to include here..
    def paint(self):
        """
        Paint this visual now.         
        """
        raise NotImplementedError



class VisualComponent(object):
    """
    Base for classes that encapsulate some modular component of a Visual.
    
    These define Functions for extending the shader code as well as an 
    activate() method that inserts these Functions into a program.
    
    VisualComponents may be considered friends of the Visual they are attached
    to; often they will need to access internal data structures of the Visual
    to make decisions about constructing shader components.
    """
    def __init__(self, visual=None):
        self._visual = None
        if visual is not None:
            self._attach(visual)
        
    @property
    def visual(self):
        """The Visual that this component is attached to."""
        return self._visual

    def _attach(self, visual):
        """Attach this component to a Visual. This should be called by the 
        Visual itself.
        """
        self._visual = visual

    def _detach(self):
        """Detach this component from its Visual.
        """
        self._visual = None
        
    def _activate(self, program):
        """Install this component into *program*. This method is called by the 
        Visual when it is ready to build its program.
        """
        raise NotImplementedError


# Import visuals in this namespace
from .points import PointsVisual  # noqa
from .line import LineVisual
