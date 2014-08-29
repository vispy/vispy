# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Line visual implementing Agg- and GL-based drawing modes.
"""

from __future__ import division

import numpy as np

from .... import gloo
from ....color import ColorArray
from ...shaders import ModularProgram, Function
from ..visual import Visual

from .dash_atlas import DashAtlas
from .vertex import VERTEX_SHADER as AGG_VERTEX_SHADER
from .fragment import FRAGMENT_SHADER as AGG_FRAGMENT_SHADER


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


"""
TODO:

* Agg support is very minimal; needs attention.
* Optimization--avoid creating new buffers, avoid triggering program
  recompile.
"""


joins = {'miter': 0, 'round': 1, 'bevel': 2}

caps = {'': 0, 'none': 0, '.': 0,
        'round': 1, ')': 1, '(': 1, 'o': 1,
        'triangle in': 2, '<': 2,
        'triangle out': 3, '>': 3,
        'square': 4, '=': 4, 'butt': 4,
        '|': 5}

_agg_vtype = np.dtype([('a_position', 'f4', 2),
                       ('a_tangents', 'f4', 4),
                       ('a_segment',  'f4', 2),
                       ('a_angles',   'f4', 2),
                       ('a_texcoord', 'f4', 2),
                       ('alength', 'f4', 1),
                       ('color', 'f4', 4)])


def _agg_bake(vertices, color, closed=False):
    """
    Bake a list of 2D vertices for rendering them as thick line. Each line
    segment must have its own vertices because of antialias (this means no
    vertex sharing between two adjacent line segments).
    """

    n = len(vertices)
    P = np.array(vertices).reshape(n, 2).astype(float)
    idx = np.arange(n)  # used to eventually tile the color array

    dx, dy = P[0] - P[-1]
    d = np.sqrt(dx*dx+dy*dy)

    # If closed, make sure first vertex = last vertex (+/- epsilon=1e-10)
    if closed and d > 1e-10:
        P = np.append(P, P[0]).reshape(n+1, 2)
        idx = np.append(idx, idx[-1])
        n += 1

    V = np.zeros(len(P), dtype=_agg_vtype)
    V['a_position'] = P

    # Tangents & norms
    T = P[1:] - P[:-1]

    N = np.sqrt(T[:, 0]**2 + T[:, 1]**2)
    # T /= N.reshape(len(T),1)
    V['a_tangents'][+1:, :2] = T
    V['a_tangents'][0, :2] = T[-1] if closed else T[0]
    V['a_tangents'][:-1, 2:] = T
    V['a_tangents'][-1, 2:] = T[0] if closed else T[-1]

    # Angles
    T1 = V['a_tangents'][:, :2]
    T2 = V['a_tangents'][:, 2:]
    A = np.arctan2(T1[:, 0]*T2[:, 1]-T1[:, 1]*T2[:, 0],
                   T1[:, 0]*T2[:, 0]+T1[:, 1]*T2[:, 1])
    V['a_angles'][:-1, 0] = A[:-1]
    V['a_angles'][:-1, 1] = A[+1:]

    # Segment
    L = np.cumsum(N)
    V['a_segment'][+1:, 0] = L
    V['a_segment'][:-1, 1] = L
    #V['a_lengths'][:,2] = L[-1]

    # Step 1: A -- B -- C  =>  A -- B, B' -- C
    V = np.repeat(V, 2, axis=0)[1:-1]
    V['a_segment'][1:] = V['a_segment'][:-1]
    V['a_angles'][1:] = V['a_angles'][:-1]
    V['a_texcoord'][0::2] = -1
    V['a_texcoord'][1::2] = +1
    idx = np.repeat(idx, 2)[1:-1]

    # Step 2: A -- B, B' -- C  -> A0/A1 -- B0/B1, B'0/B'1 -- C0/C1
    V = np.repeat(V, 2, axis=0)
    V['a_texcoord'][0::2, 1] = -1
    V['a_texcoord'][1::2, 1] = +1
    idx = np.repeat(idx, 2)

    I = np.resize(np.array([0, 1, 2, 1, 2, 3], dtype=np.uint32), (n-1)*(2*3))
    I += np.repeat(4*np.arange(n-1, dtype=np.uint32), 6)

    # Length
    V['alength'] = L[-1] * np.ones(len(V))

    # Color
    if color.ndim == 1:
        color = np.tile(color, (len(V), 1))
    elif color.ndim == 2 and len(color) == n:
        color = color[idx]
    else:
        raise ValueError('Color length %s does not match number of vertices '
                         '%s' % (len(color), n))
    V['color'] = color

    return gloo.VertexBuffer(V), gloo.IndexBuffer(I)


GL_VERTEX_SHADER = """
    varying vec4 v_color;

    void main(void)
    {
        gl_Position = $transform($position);
        v_color = $color;
    }
"""

GL_FRAGMENT_SHADER = """
    varying vec4 v_color;
    void main()
    {
        gl_FragColor = v_color;
    }
"""


class Line(Visual):
    """Line visual

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
        Mode to use for drawing.
            * "agg" uses anti-grain geometry to draw nicely antialiased lines
              with proper joins and endcaps.
            * "gl" uses OpenGL's built-in line rendering. This is much faster,
              but produces much lower-quality results and is not guaranteed to
              obey the requested line width or join/endcap styles.
    antialias : bool 
        For mode='gl', specifies whether to use line smoothing or not.
    """
    def __init__(self, pos=None, color=(0.5, 0.5, 0.5, 1), width=1,
                 connect='strip', mode='gl', antialias=False, **kwds):
        # todo: Get rid of aa argument? It's a bit awkward since ...
        # - line_smooth is not supported on ES 2.0
        # - why on earth would you turn off aa with agg?
        Visual.__init__(self, **kwds)
        self._pos = pos
        self._color = ColorArray(color)
        self._width = float(width)
        assert connect is not None  # can't be to start
        self._connect = connect
        self._mode = 'none'
        self._origs = {}
        self.antialias = antialias
        self._vbo = None
        self._I = None
        # Set up the GL program
        self._gl_program = ModularProgram(GL_VERTEX_SHADER,
                                          GL_FRAGMENT_SHADER)
        # Set up the AGG program
        self._agg_program = ModularProgram(AGG_VERTEX_SHADER,
                                           AGG_FRAGMENT_SHADER)
        # agg attributes
        self._da = None
        self._U = None
        self._dash_atlas = None
        
        # now actually set the mode, which will call set_data
        self.mode = mode

    @property
    def antialias(self):
        return self._antialias

    @antialias.setter
    def antialias(self, aa):
        self._antialias = bool(aa)
        self.update()

    @property
    def mode(self):
        """The current drawing mode"""
        return self._mode

    @mode.setter
    def mode(self, mode):
        if mode not in ('agg', 'gl'):
            raise ValueError('mode argument must be "agg" or "gl".')
        if mode == self._mode:
            return
        # If the mode changed, reset everything
        self._mode = mode
        if self._mode == 'agg' and self._da is None:
            self._da = DashAtlas()
            dash_index, dash_period = self._da['solid']
            self._U = dict(dash_index=dash_index, dash_period=dash_period,
                           linejoin=joins['round'],
                           linecaps=(caps['round'], caps['round']),
                           dash_caps=(caps['round'], caps['round']),
                           linewidth=self._width, antialias=1.0)
            self._dash_atlas = gloo.Texture2D(self._da._data)
            
        # do not call subclass set_data; this is often overridden with a 
        # different signature.
        Line.set_data(self, self._pos, self._color, self._width, self._connect)

    def set_data(self, pos=None, color=None, width=None, connect=None):
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
            * int numpy arrays specify the exact set of segment pairs to
              connect.
            * bool numpy arrays specify which _adjacent_ pairs to connect.
        """
        if isinstance(connect, np.ndarray) and connect.dtype == bool:
            connect = self._convert_bool_connect(connect)
        
        self._origs = {'pos': pos, 'color': color, 
                       'width': width, 'connect': connect}
        
        if color is not None:
            self._color = ColorArray(color).rgba
            if len(self._color) == 1:
                self._color = self._color[0]
                
        if width is not None:
            self._width = width
            
        if self.mode == 'gl':
            self._gl_set_data(**self._origs)
        else:
            self._agg_set_data(**self._origs)

    def _convert_bool_connect(self, connect):
        # Convert a boolean connection array to a vertex index array
        assert connect.ndim == 1
        index = np.empty((len(connect), 2), dtype=np.uint32)
        index[:] = np.arange(len(connect))[:, np.newaxis]
        index[:, 1] += 1
        return index[connect]
            
    def _gl_set_data(self, pos, color, width, connect):
        if connect is not None:
            if isinstance(connect, np.ndarray):
                self._connect = gloo.IndexBuffer(connect.astype(np.uint32))
            else:
                self._connect = connect
        if pos is not None:
            self._pos = pos
            pos_arr = np.asarray(pos, dtype=np.float32)
            vbo = gloo.VertexBuffer(pos_arr)
            if pos_arr.shape[-1] == 2:
                self._pos_expr = vec2to4(vbo)
            elif pos_arr.shape[-1] == 3:
                self._pos_expr = vec3to4(vbo)
            else:
                raise TypeError("pos array should have 2 or 3 elements in last"
                                " axis. shape=%r" % pos_arr.shape)
            self._vbo = vbo
        else:
            self._pos = None
        self.update()

    def _agg_set_data(self, pos, color, width, connect):
        if connect is not None:
            if connect != 'strip':
                raise NotImplementedError("Only 'strip' connection mode "
                                          "allowed for agg-mode lines.")
            self._connect = connect
        if pos is not None:
            self._pos = pos
            self._vbo, self._I = _agg_bake(pos, self._color)
        else:
            self._pos = None

        self.update()

    def bounds(self, mode, axis):
        if 'pos' not in self._origs:
            return None
        data = self._origs['pos']
        if data.shape[1] > axis:
            return (data[:, axis].min(), data[:, axis].max())
        else:
            return (0, 0)

    def draw(self, event):
        if self.mode == 'gl':
            self._gl_draw(event)
        else:
            self._agg_draw(event)

    def _gl_draw(self, event):
        if self._pos is None:
            return
        xform = event.render_transform.shader_map()
        self._gl_program.vert['transform'] = xform
        self._gl_program.vert['position'] = self._pos_expr
        if self._color.ndim == 1:
            self._gl_program.vert['color'] = self._color
        else:
            self._gl_program.vert['color'] = gloo.VertexBuffer(self._color)
        gloo.set_state('translucent')
        
        # Do we want to use OpenGL, and can we?
        GL = None
        if self._width > 1 or self._antialias:
            try:
                import OpenGL.GL as GL
            except ImportError:
                pass
        
        # Turn on line smooth and/or line width
        if GL:
            if self._antialias:
                GL.glEnable(GL.GL_LINE_SMOOTH)
            if GL and self._width > 1:
                GL.glLineWidth(self._width)
        
        # Draw
        if self._connect == 'strip':
            self._gl_program.draw('line_strip')
        elif self._connect == 'segments':
            self._gl_program.draw('lines')
        elif isinstance(self._connect, gloo.IndexBuffer):
            self._gl_program.draw('lines', self._connect)
        else:
            raise ValueError("Invalid line connect mode: %r" % self._connect)
        
        # Turn off line smooth and/or line width
        if GL:
            if self._antialias:
                GL.glDisable(GL.GL_LINE_SMOOTH)
            if GL and self._width > 1:
                GL.glLineWidth(1)

    def _agg_draw(self, event):
        if self._pos is None:
            return
        gloo.set_state('translucent', depth_test=False)
        data_doc = event.document_transform()
        doc_px = event.entity_transform(map_from=event.document_cs,
                                        map_to=event.framebuffer_cs)
        px_ndc = event.entity_transform(map_from=event.framebuffer_cs,
                                        map_to=event.render_cs)
        vert = self._agg_program.vert
        vert['doc_px_transform'] = doc_px.shader_map()
        vert['px_ndc_transform'] = px_ndc.shader_map()
        vert['transform'] = data_doc.shader_map()
        self._agg_program.prepare()
        self._agg_program.bind(self._vbo)
        uniforms = dict(closed=False, miter_limit=4.0, dash_phase=0.0)
        for n, v in uniforms.items():
            self._agg_program[n] = v
        for n, v in self._U.items():
            self._agg_program[n] = v
        self._agg_program['u_dash_atlas'] = self._dash_atlas
        self._agg_program.draw('triangles', self._I)
