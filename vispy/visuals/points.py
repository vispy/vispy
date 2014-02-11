# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .. import gloo
from . import BaseVisual


class PointsVisual(BaseVisual):

    """ PointsVisual(N=1000)
    A simple visual that shows a random set of points. N can also be
    a numpy array of positions.

    """

    VERT_SHADER = """
        // Stuff that each visual must have ...
        uniform   mat4 transform_model;
        uniform   mat4 transform_view;
        uniform   mat4 transform_projection;


        attribute vec3 a_position;

        varying vec4 v_color;
        void main (void) {
            gl_Position = vec4(a_position, 1.0);
            gl_Position = transform_projection * transform_view
                        * transform_model * gl_Position;
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

    def __init__(self, N=1000):
        BaseVisual.__init__(self)

        if isinstance(N, np.ndarray):
            data = N
        elif isinstance(N, int):
            data = np.random.uniform(0, 400, (N, 3)).astype('float32')
        else:
            raise ValueError('Invalid value for N.')

        # Create and attach vertex buffer
        self.program['a_position'] = gloo.VertexBuffer(data)
