# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .. import gloo
from .visual import Visual
from .components import (XYPosComponent, XYZPosComponent, 
                         UniformColorComponent, VertexColorComponent)


class PointVisual(Visual):
    """
    Displays multiple point sprites.
    """
    def __init__(self, pos=None, **kwds):
        super(PointVisual, self).__init__()
        
        glopts = kwds.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)
        
        if kwds:
            self.set_data(pos, **kwds)
            
        # TODO: turn this into a proper component.
        code = """
        void $set_point_size() {
            gl_PointSize = 10.0; //size;
        }
        """
        self._program.add_callback('vert_post_hook', Function(code))

    def set_data(self, pos=None, z=0.0, color=(1,1,1,1)):
        """
        *pos* must be array of shape (..., 2) or (..., 3).
        *z* is only used in the former case.
        """
        # select input component based on pos.shape
        if pos is not None:
            if pos.shape[-1] == 2:
                if not isinstance(self.pos_component, XYPosComponent):
                    self.pos_component = XYPosComponent()
                self.pos_component.set_data(xy=pos, z=z)
            elif pos.shape[-1] == 3:
                if not isinstance(self.pos_component, XYZPosComponent):
                    self.pos_component = XYZPosComponent()
                self.pos_component.set_data(pos=pos)
            
        if isinstance(color, tuple):
            self.fragment_components = [UniformColorComponent(color)]
        elif isinstance(color, np.ndarray):
            self.fragment_components = [VertexColorComponent(color)]
            
    @property
    def primitive(self):
        return gloo.gl.GL_POINTS

    def paint(self):
        gloo.gl.glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
        gloo.gl.glEnable(GL_POINT_SPRITE)
        super(PointVisual, self).paint()
        

## -*- coding: utf-8 -*-
## Copyright (c) 2014, Vispy Development Team.
## Distributed under the (new) BSD License. See LICENSE.txt for more info.

#from __future__ import division

#import numpy as np

#from .. import gloo
#from .visual import Visual
#from .transforms import AffineTransform
#from ..shaders.composite import ModularProgram


## HACK: True OpenGL ES does not need to enable point sprite and does not define
## these two constants. Desktop OpenGL needs to enable these two modes but we do
## not have these two constants because our GL namespace pretends to be ES.
#GL_VERTEX_PROGRAM_POINT_SIZE = 34370
#GL_POINT_SPRITE = 34913

#class PointsVisual(Visual):

    #""" PointsVisual(N=1000)
    #A simple visual that shows a random set of points. N can also be
    #a numpy array of positions.

    #"""

    #VERT_SHADER = """
        #void post_hook();
        #vec4 map_local_to_nd(vec4);
        
        #attribute vec3 a_position;

        #varying vec4 v_color;
        #void main (void) {
            #vec4 pos = vec4(a_position, 1.0);
            #gl_Position = map_local_to_nd(pos);
            #v_color = vec4(1.0, 0.5, 0.0, 0.8);
            #gl_PointSize = 10.0; //size;
        #}
    #"""

    #FRAG_SHADER = """
        #varying vec4 v_color;
        #void main()
        #{
            #float x = 2.0*gl_PointCoord.x - 1.0;
            #float y = 2.0*gl_PointCoord.y - 1.0;
            #float a = 1.0 - (x*x + y*y);
            #gl_FragColor = vec4(v_color.rgb, a*v_color.a);
        #}
    #"""

    #def __init__(self, pos):
        #super(PointsVisual, self).__init__()
        #self.set_gl_options('additive')
        
        #self.pos = pos
        #self._vbo = None
        #self._program = None
        #self.transform = AffineTransform()

    #def _build_vbo(self):
        #self._vbo = gloo.VertexBuffer(self.pos)
        
    #def _build_program(self):
        
        ## Create composite program
        #self._program = ModularProgram(vmain=self.VERT_SHADER, 
                                         #fmain=self.FRAG_SHADER)
        
        ## Attach transformation function
        #self._program['map_local_to_nd'] = self.transform.shader_map()
        
        
    #def paint(self):
        #super(PointsVisual, self).paint()
        
        #if self.pos is None or len(self.pos) == 0:
            #return
        
        #if self._program is None:
            #self._build_program()
            
        #if self._vbo is None:
            #self._build_vbo()
        #self._program['a_position'] = self._vbo
        
        ## HACK: True OpenGL ES does not need to enable point sprite and does not define
        ## these two constants. Desktop OpenGL needs to enable these two modes but we do
        ## not have these two constants because our GL namespace pretends to be ES.
        #gloo.gl.glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
        #gloo.gl.glEnable(GL_POINT_SPRITE)
        
        #self._program.draw(gloo.gl.GL_POINTS)
        