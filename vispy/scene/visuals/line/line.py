# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Line visual implementing Agg- and GL-based drawing modes.

TODO: 

* Agg support is very minimal; needs attention.
* Optimization--avoid creating new buffers, avoid triggering program 
  recompile.
  
"""

from __future__ import division

import numpy as np

from .... import gloo
from ....color import Color
from ...shaders import ModularProgram, Function
from ..visual import Visual
from .line_agg import LineAgg

try:
    import OpenGL.GL
    HAVE_PYOPENGL = True
except ImportError:
    HAVE_PYOPENGL = False


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

    def __init__(self, pos=None, color=(0.5, 0.5, 0.5, 1), width=1, 
                 connect='strip', mode='agg', antialias=True, **kwds):
        Visual.__init__(self, **kwds)
        
        # todo: move this to set_data and allow mode switch after init
        if mode not in ('agg', 'gl'):
            raise ValueError('mode argument must be "agg" or "gl".')
        self._mode = mode
        
        self._vbo = None
        self._color = None
        self._pos_expr = None
        self._connect = None
        self._width = None
        self._antialias = antialias
        
        # Reference to a LineAgg visual that will do our drawing if mode=='agg'
        # todo: this is a bit of a hack to get agg and gl_lines available via
        # the same class. It can probably be cleaned up..
        self._agg_line = None
        
        self._program = ModularProgram(self.VERTEX_SHADER,
                                       self.FRAGMENT_SHADER)
        self.set_data(pos, color, width, connect)

    @property
    def antialias(self):
        return self._antialias
    
    @antialias.setter
    def antialias(self, aa):
        self._antialias = aa
        self.update()

    def set_data(self, pos=None, color=None, width=None, connect=None, mode=None):
        """ Set the data used to draw this visual.
        
        Parameters
        ----------
        pos : array 
            Array of shape (..., 2) or (..., 3) specifying vertex coordinates.
        color : Color, tuple, or array
            The color to use when drawing the line. If an array is given, it
            must be of shape (..., 4) and provide one rgba color per vertex.
        width:
            The width of the line in px. Line widths > 1px are only
            guaranteed to work when using 'agg' mode. 
        connect : str or array
            Determines which vertices are connected by lines.
            * "strip" causes the line to be drawn with each vertex 
              connected to the next.
            * "segments" causes each pair of vertices to draw an 
              independent line segment
            * numpy arrays specify the exact set of segment pairs to 
              connect.
        mode : str
            * "agg" uses anti-grain geometry to draw nicely antialiased lines
              with proper joins and endcaps. 
            * "gl" uses OpenGL's built-in line rendering. This is much faster,
              but produces much lower-quality results and is not guaranteed to
              obey the requested line width or join/endcap styles.
        """
        if mode is not None:
            raise NotImplementedError("Line mode can only be set during "
                                      "initialization (for now).")

        if self._mode == 'agg':
            # use a separate method for updating agg lines
            self._agg_set_data(pos, color, width, connect)
            return
        
        # for non-agg lines:

        if width is not None:
            self._width = width
        
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

    def _agg_set_data(self, pos=None, color=None, width=None, connect=None):
        if connect is not None:
            if connect != 'strip':
                raise NotImplementedError("Only 'strip' connection mode "
                                          "allowed for agg-mode lines.")
            self._connect = connect
        
        if color is not None:
            self._color = color
            
        if width is not None:
            self._width = width
        
        style = {
            'color': self._color,
            'width': self._width,
            'antialias': self._antialias,
        }
        if pos is not None:
            self._agg_line = LineAgg(path=pos, **style)
        else:
            self._agg_line = None
        self.update()

    def draw(self, event):
        if self._mode == 'agg':
            self._agg_draw(event)
            return
        
        if self._pos_expr is None:
            return
        
        xform = event.render_transform.shader_map()
        self._program.vert['transform'] = xform
        self._program.vert['position'] = self._pos_expr
        self._program.vert['color'] = self._color
        
        gloo.set_state('translucent')

        if HAVE_PYOPENGL:
            OpenGL.GL.glLineWidth(self._width)
            if self._antialias:
                OpenGL.GL.glEnable(OpenGL.GL.GL_LINE_SMOOTH)
            else:
                OpenGL.GL.glDisable(OpenGL.GL.GL_LINE_SMOOTH)
        
        if self._connect == 'strip':
            self._program.draw('line_strip')
        elif self._connect == 'segments':
            self._program.draw('lines')
        elif isinstance(self._connect, gloo.IndexBuffer):
            self._program.draw('lines', self._connect)
        else:
            raise ValueError("Invalid line connect mode: %r" % self._connect)

    def _agg_draw(self, event):
        if self._agg_line is None:
            return
        self._agg_line.transform = self.transform
        self._agg_line.draw(event)
