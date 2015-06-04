# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Arrows are a subclass of line visuals, which adds the ability to put several
heads on a line.
"""

from __future__ import division

import numpy as np

from ... import glsl, gloo
from ...util.profiler import Profiler
from ..shaders import ModularProgram
from .line import LineVisual

import OpenGL
OpenGL.ERROR_LOGGING = True


ARROW_TYPES = [
    'stealth',
    'curved',
    'angle_30',
    'angle_60',
    'angle_90',
    'triangle_30',
    'triangle_60',
    'triangle_90'
]


class ArrowVisual(LineVisual):
    """ArrowVisual: lines with one or more heads

    Parameters
    ----------
    pos : array
        Array of shape (..., 2) specifying vertex coordinates. Note that for
        the arrow visual the dimension is currently limited to 2D.
    color : Color, tuple, or array
        The color to use when drawing the line. If an array is given, it
        must be of shape (..., 4) and provide one rgba color per vertex.
        Can also be a colormap name, or appropriate `Function`.
    width:
        The width of the line in px. Line widths > 1px are only
        guaranteed to work when using 'agg' method.
    connect : str or array
        Determines which vertices are connected by lines.

            * "strip" causes the line to be drawn with each vertex
              connected to the next.
            * "segments" causes each pair of vertices to draw an
              independent line segment
            * numpy arrays specify the exact set of segment pairs to
              connect.

    method : str
        Mode to use for drawing.

            * "agg" uses anti-grain geometry to draw nicely antialiased lines
              with proper joins and endcaps.
            * "gl" uses OpenGL's built-in line rendering. This is much faster,
              but produces much lower-quality results and is not guaranteed to
              obey the requested line width or join/endcap styles.

    antialias : bool
        Enables or disables antialiasing.
        For method='gl', this specifies whether to use GL's line smoothing,
        which may be unavailable or inconsistent on some platforms.

    arrows : array-like
        Specifies which line segements get an arrow head. It should be an
        iterable containing pairs of vertices which determine the arrow body.
        The arrow head will be attached to the last vertex of the pair. The
        vertices must be of the shape (..., 2).

    arrow_type : str
        Specifies how the arrow heads should look like. See `ARROW_TYPES` for
        the available arrow head types.
    """

    ARROWHEAD_VERTEX_SHADER = glsl.get('arrowheads/arrowheads.vert')
    ARROWHEAD_FRAGMENT_SHADER = glsl.get('arrowheads/arrowheads.frag')

    _arrow_vtype = np.dtype([
        ('v1', 'f4', 2),
        ('v2', 'f4', 2),
        ('size', 'f4', 1),
        ('color', 'f4', 4),
        ('linewidth', 'f4', 1)
    ])

    def __init__(self, pos=None, color=(0.5, 0.5, 0.5, 1), width=1,
                 connect='strip', method='gl', antialias=False, arrows=None,
                 arrow_type='stealth', arrow_size=None):

        LineVisual.__init__(self, pos, color, width, connect, method,
                            antialias)

        self._arrow_type = None
        self._arrow_size = None
        self._arrows = None
        self.arrow_type = arrow_type
        self.arrow_size = arrow_size
        self.set_data(arrows=arrows)

        self._arrow_vbo = gloo.VertexBuffer()
        self._arrow_program = ModularProgram(self.ARROWHEAD_VERTEX_SHADER,
                                             self.ARROWHEAD_FRAGMENT_SHADER)

    def set_data(self, pos=None, color=None, width=None, connect=None,
                 arrows=None):
        """Set the data used to draw this visual.

        Parameters
        ----------
        pos : array
            Array of shape (..., 2) or (..., 3) specifying vertex coordinates.
        color : Color, tuple, or array
            The color to use when drawing the line. If an array is given, it
            must be of shape (..., 4) and provide one rgba color per vertex.
        width:
            The width of the line in px. Line widths > 1px are only
            guaranteed to work when using 'agg' method.
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

        LineVisual.set_data(self, pos, color, width, connect)

        if arrows is not None:
            self._arrows = arrows
            self._changed['arrows'] = True

        self.update()

    @property
    def arrow_type(self):
        return self._arrow_type

    @arrow_type.setter
    def arrow_type(self, value):
        if value not in ARROW_TYPES:
            raise ValueError(
                "Invalid arrow type '{}'. Should be one of {}".format(
                    value, ", ".join(ARROW_TYPES)
                )
            )

        if value == self._arrow_type:
            return

        self._arrow_type = value
        self._changed['arrows'] = True

    @property
    def arrow_size(self):
        return self._arrow_size

    @arrow_size.setter
    def arrow_size(self, value):
        if value is None:
            self._arrow_size = 5.0
        else:
            self._arrow_size = value

    def draw(self, transforms):
        prof = Profiler()

        # Keep backup of changed dict as it is reset by LineVisual
        changed = self._changed.copy()
        LineVisual.draw(self, transforms)

        if changed['arrows']:
            V = self._prepare_vertex_data()
            self._arrow_vbo.set_data(V)
            print(V)

        self._arrow_program.bind(self._arrow_vbo)
        prof('arrowhead prepare')

        xform = transforms.get_full_transform()
        self._arrow_program['antialias'] = 1.0
        self._arrow_program.vert['transform'] = xform
        self._arrow_program.frag['arrow_type'] = self._arrow_type

        self._arrow_program.draw('points')
        prof('arrowhead draw')

    def _prepare_vertex_data(self):
        num_arrows = len(self._arrows)
        V = np.zeros(num_arrows, dtype=self._arrow_vtype)
        arrows = np.array(self._arrows).astype(float)

        # Create matrix with column 0 and 1 representing v1.x and v1.y
        # and column 2 and 3 represents v2.x and v2.y
        arrows = arrows.reshape((num_arrows, arrows.shape[1] * 2))

        print("Num:", num_arrows)
        print(arrows)
        print("arrows 0", arrows[0, 0:2])
        print("arrows 1", arrows[0, 2:4])

        V['v1'] = arrows[:, 0:2]
        V['v2'] = arrows[:, 2:4]

        V['size'][:] = self._arrow_size
        V['color'][:] = self._interpret_color()
        V['linewidth'][:] = self._width

        return V
