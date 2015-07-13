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
from ..visual import Visual
from ..markers import MarkersVisual
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
    'triangle_90',
    'inhibitor_round'
]


FILL_TYPES = [
    'filled',
    'outline',
    'stroke'
]


class _ArrowHeadVisual(Visual):
    """
    ArrowHeadVisual: several shapes to put on the end of a line.
    This visual differs from MarkersVisual in the sense that this visual
    calculates the orientation of the visual on the GPU, by calculating the
    tangent of the line between two given vertices.

    This is not really a visual you would use on your own,
    use :class:`ArrowVisual` instead.

    Parameters
    ----------
    parent : ArrowVisual
        This actual ArrowVisual this arrow head is part of.
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

    def __init__(self, parent):

        Visual.__init__(self, self.ARROWHEAD_VERTEX_SHADER,
                        self.ARROWHEAD_FRAGMENT_SHADER)

        self._parent = parent
        self._arrow_vbo = gloo.VertexBuffer()
        self._vshare.draw_mode = 'points'

    def _prepare_transforms(self, view):
        xform = view.transforms.get_transform()
        view.view_program.vert['transform'] = xform

    def _prepare_draw(self, view=None):

        if self._parent._arrows_changed:
            v = self._prepare_vertex_data()
            print(v)
            self._arrow_vbo.set_data(v)

        self.shared_program.bind(self._arrow_vbo)

        self.shared_program['antialias'] = 1.0
        self.shared_program.frag['arrow_type'] = self._parent.arrow_type
        self.shared_program.frag['fill_type'] = self._parent.fill_type

    def _prepare_vertex_data(self):
        num_arrows = len(self._parent.arrows)
        v = np.zeros(num_arrows, dtype=self._arrow_vtype)
        arrows = np.array(self._parent.arrows).astype(float)

        # Create matrix with column 0 and 1 representing v1.x and v1.y
        # and column 2 and 3 represents v2.x and v2.y
        arrows = arrows.reshape((num_arrows, arrows.shape[1] * 2))

        v['v1'] = arrows[:, 0:2]
        v['v2'] = arrows[:, 2:4]

        v['size'][:] = self._parent.arrow_size
        v['color'][:] = self._parent._interpret_color()
        v['linewidth'][:] = self._parent.width

        return v


class ArrowVisual(LineVisual):
    """ArrowVisual

    A special line visual which can also draw optional arrow heads at the
    specified vertices.

    Parameters
    ----------
    """

    def __init__(self, pos=None, color=(0.5, 0.5, 0.5, 1), width=1,
                 connect='strip', method='gl', antialias=False, arrows=None,
                 arrow_type='stealth', arrow_size=None, fill_type="filled"):

        # Do not use the self._changed dictionary as it gets overwritten by
        # the LineVisual constructor.
        self._arrows_changed = False

        self._arrow_type = None
        self._arrow_size = None
        self._fill_type = None
        self._arrows = None

        self.arrow_type = arrow_type
        self.arrow_size = arrow_size
        self.fill_type = fill_type

        # TODO: `LineVisual.__init__` also calls its own `set_data` method,
        # which triggers an *update* event. This results in a redraw. After
        # that we call our own `set_data` method, which triggers another
        # redraw. This should be fixed.
        LineVisual.__init__(self, pos, color, width, connect, method,
                            antialias)
        ArrowVisual.set_data(self, arrows=arrows)

        # Add marker visual for the arrow head
        self.arrow_head = _ArrowHeadVisual(self)
        self.add_subvisual(self.arrow_head)

    def set_data(self, pos=None, color=None, width=None, connect=None,
                 arrows=None, _update=True):
        """Set the data used for this visual

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
        arrows : array-like
            Specifies which line segments get an arrow head. It should be an
            iterable containing pairs of vertices which determine the arrow
            body. The arrow head will be attached to the last vertex of the
            pair. The vertices must be of the shape (..., 2). The reason you
            need to specify two vertices for a single arrow head is that we
            need to determine the orientation of the arrow head.
        """

        if arrows is not None:
            self._arrows = arrows
            self._arrows_changed = True

        LineVisual.set_data(self, pos, color, width, connect)

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
        self._arrows_changed = True

    @property
    def arrow_size(self):
        return self._arrow_size

    @arrow_size.setter
    def arrow_size(self, value):
        if value is None:
            self._arrow_size = 5.0
        else:
            self._arrow_size = value

        self._arrows_changed = True

    @property
    def fill_type(self):
        return self._fill_type

    @fill_type.setter
    def fill_type(self, value):
        if value not in FILL_TYPES:
            raise ValueError(
                "Invalid fill type '{}'. Should be one of {}".format(
                    value, ", ".join(FILL_TYPES)
                )
            )

        if value == self._fill_type:
            return

        self._fill_type = value
        self._arrows_changed = True

    @property
    def arrows(self):
        return self._arrows
