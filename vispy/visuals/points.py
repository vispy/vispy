# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .. import gloo
from . import Visual
from .transforms import AffineTransform
from ..shaders.composite import CompositeProgram

class PointsVisual(Visual):

    """ PointsVisual(N=1000)
    A simple visual that shows a random set of points. N can also be
    a numpy array of positions.

    """

    VERT_SHADER = """
        void post_hook();
        vec4 map_local_to_nd(vec4);
        
        attribute vec3 a_position;

        varying vec4 v_color;
        void main (void) {
            vec4 pos = vec4(a_position, 1.0);
            gl_Position = map_local_to_nd(pos);
            v_color = vec4(1.0, 0.5, 0.0, 0.8);
            gl_PointSize = 10.0; //size;
        }
    """

    FRAG_SHADER = """
        varying vec4 v_color;
        void main()
        {
            float x = 2.0*gl_PointCoord.x - 1.0;
            float y = 2.0*gl_PointCoord.y - 1.0;
            float a = 1.0 - (x*x + y*y);
            gl_FragColor = vec4(v_color.rgb, a*v_color.a);
        }
    """

    def __init__(self, pos):
        super(PointsVisual, self).__init__()

        self.pos = pos
        self._vbo = None
        self._program = None
        self.transform = AffineTransform()

    def _build_vbo(self):
        self._vbo = gloo.VertexBuffer(self.pos)
        
    def _build_program(self):
        
        # Create composite program
        self._program = CompositeProgram(vmain=self.VERT_SHADER, 
                                         fmain=self.FRAG_SHADER)
        
        # Attach transformation function
        tr_bound = self.transform.wrap_map('map_local_to_nd')
        self._program.set_hook('map_local_to_nd', tr_bound)
        
        
    def paint(self):
        super(PointsVisual, self).paint()
        
        if self.pos is None or len(self.pos) == 0:
            return
        
        if self._program is None:
            self._build_program()
            
        if self._vbo is None:
            self._build_vbo()
        self._program['a_position'] = self._vbo
        
        self._program.draw('POINTS')
        