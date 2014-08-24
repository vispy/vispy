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

from vispy import gloo
from ...color import Color
from ..shaders import ModularProgram, Function
from .visual import Visual


vec2to4 = Function("""
    vec4 vec2to4(vec2 input) {
        return vec4(input, 0, 1);
    }
""")

vec3to4 = Function("""
    vec4 vec3to4(vec3 input) {
        return vec4(input, 1);
    }
""")

class Line(Visual):
    VERTEX_SHADER = """
        varying vec4 v_color;
        
        void main(void)
        {
            gl_Position = $transform($position);
            v_color = $color;
        }
    """

    FRAGMENT_SHADER = """
        varying vec4 v_color;
        void main()
        {
            gl_FragColor = v_color;
        }
    """

    def __init__(self, pos=None, color=None, connect='strip', **kwds):
        Visual.__init__(self, **kwds)
        
        self._vbo = None
        self._color = None
        self._pos_expr = None
        self._connect = None
        
        self._program = ModularProgram(self.VERTEX_SHADER,
                                       self.FRAGMENT_SHADER)
        self.set_data(pos=pos, color=color, connect=connect)

    def set_data(self, pos=None, color=None, connect=None):
        """ Set the data used to draw this visual.
        
        Parameters
        ----------
        pos : array 
            Array of shape (..., 2) or (..., 3) specifying vertex coordinates.
        color : Color, tuple, or array
            The color to use when drawing the line. If an array is given, it
            must be of shape (..., 4) and provide one rgba color per vertex.
        connect : str or array
            Determines which vertices are connected by lines.
            * "strip" causes the line to be drawn with each vertex 
                connected to the next.
            * "segments" causes each pair of vertices to draw an 
                independent line segment
            * numpy arrays specify the exact set of segment pairs to 
                connect.
        """
        if pos is not None:
            vbo = gloo.VertexBuffer(np.asarray(pos, dtype=np.float32))
            if pos.shape[-1] == 2:
                self._pos_expr = vec2to4(vbo)
            elif pos.shape[-1] == 3:
                self._pos_expr = vec3to4(vbo)
            else:
                raise TypeError("pos array should have 2 or 3 elements in last"
                                " axis.")
            self._vbo = vbo
        
        if color is not None:
            if isinstance(color, np.ndarray) and color.ndim > 1:
                self._color = gloo.VertexBuffer(color.astype(np.float32))
            else:
                self._color = Color(color).rgba
                
        if connect is not None:
            if isinstance(connect, np.ndarray):
                self._connect = gloo.IndexBuffer(connect.astype(np.uint32))
            else:
                self._connect = connect
            
        self.update()

    def draw(self, event):
        if self._pos_expr is None:
            return
        
        xform = event.render_transform.shader_map()
        self._program.vert['transform'] = xform
        self._program.vert['position'] = self._pos_expr
        self._program.vert['color'] = self._color
        
        gloo.set_state('translucent')
        
        if self._connect == 'strip':
            self._program.draw('line_strip')
        elif self._connect == 'segments':
            self._program.draw('lines')
        elif isinstance(self._connect, gloo.IndexBuffer):
            self._program.draw('lines', self._connect)
        else:
            raise ValueError("Invalid line connect mode: %r" % self._connect)
