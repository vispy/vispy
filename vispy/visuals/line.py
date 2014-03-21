# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple visual based on GL_LINE_STRIP / GL_LINES


API issues to work out:

  * Currently this only uses GL_LINE_STRIP. Should add a 'method' argument like
    ImageVisual.method that can be used to select higher-quality triangle 
    methods.
    
  * Add a few different position input components:
        - X values from vertex buffer of index values, Xmin, and Xstep
        - position from float texture
        
    
"""

from __future__ import division

import numpy as np

from .. import gloo
from .visual import Visual
from .components import (XYPosComponent, XYZPosComponent, 
                         UniformColorComponent, VertexColorComponent)


class LineVisual(Visual):
    """
    Displays multiple line segments.
    """
    def __init__(self, pos=None, **kwds):
        super(LineVisual, self).__init__()
        
        glopts = kwds.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)
        
        if pos is not None or kwds:
            self.set_data(pos, **kwds)

    def set_data(self, pos=None, **kwds):
        kwds['index'] = kwds.pop('edges', kwds.get('index', None))
        super(LineVisual, self).set_data(pos, **kwds)
    #def set_data(self, pos=None, edges=None, z=0.0, color=(1,1,1,1)):
        #"""
        #*pos* must be array of shape (..., 2) or (..., 3).
        #*z* is only used in the former case.
        #"""
        ## select input component based on pos.shape
        #if pos is not None:
            #if pos.shape[-1] == 2:
                #if not isinstance(self.pos_component, XYPosComponent):
                    #self.pos_component = XYPosComponent()
                #self.pos_component.set_data(xy=pos, z=z, index=edges)
            #elif pos.shape[-1] == 3:
                #if not isinstance(self.pos_component, XYZPosComponent):
                    #self.pos_component = XYZPosComponent()
                #self.pos_component.set_data(pos=pos, index=edges)
            
        #if isinstance(color, tuple):
            #self.fragment_components = [UniformColorComponent(color)]
        #elif isinstance(color, np.ndarray):
            #self.fragment_components = [VertexColorComponent(color)]
            
    @property
    def primitive(self):
        # TODO: add support for GL_LINES, GL_TRIANGLES
        return gloo.gl.GL_LINE_STRIP

