# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Arrows are a subclass of line visuals, which adds the ability to put several
heads on a line.
"""

from __future__ import division

import numpy as np

from ... import glsl, gloo
from ..transforms._util import as_vec4
from ..visual import Visual
from .line import LineVisual


ARROW_TYPES = (
    'stealth',
    'curved',
    'angle_30',
    'angle_60',
    'angle_90',
    'triangle_30',
    'triangle_60',
    'triangle_90',
    'inhibitor_round'
)


class _ArrowHeadVisual(Visual):
    """Arrow head visual

    Several shapes to put on the end of a line. This visual differs from
    MarkersVisual in the sense that this visual calculates the orientation of
    the visual on the GPU, by calculating the tangent of the line between two
    given vertices.

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
        ('v1', np.float32, (4,)),
        ('v2', np.float32, (4,)),
        ('size', np.float32),
        ('color', np.float32, (4,)),
        ('linewidth', np.float32)
    ])

    def __init__(self, parent):
        Visual.__init__(self, self.ARROWHEAD_VERTEX_SHADER,
                        self.ARROWHEAD_FRAGMENT_SHADER)
        self._parent = parent
        self.set_gl_state(depth_test=False, blend=True,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))
        self._draw_mode = 'points'

        self._arrow_vbo = gloo.VertexBuffer(
            np.array([], dtype=self._arrow_vtype))

    def _prepare_transforms(self, view):
        xform = view.transforms.get_transform()
        view.view_program.vert['transform'] = xform

    def _prepare_draw(self, view=None):
        if self._parent._arrows_changed:
            self._prepare_vertex_data()
        self.shared_program.bind(self._arrow_vbo)
        self.shared_program['antialias'] = 1.0
        self.shared_program.frag['arrow_type'] = self._parent.arrow_type
        self.shared_program.frag['fill_type'] = "filled"

    def _prepare_vertex_data(self):
        arrows = self._parent.arrows

        if arrows is None or arrows.size == 0:
            self._arrow_vbo = gloo.VertexBuffer(
                np.array([], dtype=self._arrow_vtype))
            return

        v = np.zeros(len(arrows), dtype=self._arrow_vtype)
        # 2d // 3d v1 v2.
        sh = int(arrows.shape[1] / 2)
        v['v1'] = as_vec4(arrows[:, 0:sh])
        v['v2'] = as_vec4(arrows[:, sh:int(2 * sh)])
        v['size'][:] = self._parent.arrow_size
        color, cmap = self._parent._interpret_color(self._parent.arrow_color)
        v['color'][:] = color
        v['linewidth'][:] = self._parent.width
        self._arrow_vbo = gloo.VertexBuffer(v)


class ArrowVisual(LineVisual):
    """Arrow visual

    A special line visual which can also draw optional arrow heads at the
    specified vertices.

    You add an arrow head by specifying two vertices `v1` and `v2` which
    represent the arrow body. This visual will draw an arrow head using `v2`
    as center point, and the orientation of the arrow head is automatically
    determined by calculating the direction vector between `v1` and `v2`. 
    The arrow head can be detached from arrow body.

    Parameters
    ----------
    pos : array
        Array of shape (..., 2) or (..., 3) specifying vertex coordinates
        of arrow body.
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
    arrows : array
        A (N, 4) or (N, 6) matrix where each row contains the (x, y) or the
        (x, y, z) coordinates of the first and second vertex of the arrow
        head. Remember that the second vertex is used as center point for
        the arrow head, and the first vertex is only used for determining
        the arrow head orientation.
    arrow_type : string
        Specify the arrow head type, the currently available arrow head types
        are:

            * stealth
            * curved
            * triangle_30
            * triangle_60
            * triangle_90
            * angle_30
            * angle_60
            * angle_90
            * inhibitor_round
    arrow_size : float
        Specify the arrow size
    arrow_color : Color, tuple, or array
        The arrow head color. If an array is given, it must be of shape
        (..., 4) and provide one rgba color per arrow head. Can also be a
        colormap name, or appropriate `Function`.
    """

    def __init__(self, pos=None, color=(0.5, 0.5, 0.5, 1), width=1,
                 connect='strip', method='gl', antialias=False, arrows=None,
                 arrow_type='stealth', arrow_size=None,
                 arrow_color=(0.5, 0.5, 0.5, 1)):

        # Do not use the self._changed dictionary as it gets overwritten by
        # the LineVisual constructor.
        self._arrows_changed = False

        self._arrow_type = None
        self._arrow_size = None
        self._arrows = None

        self.arrow_type = arrow_type
        self.arrow_size = arrow_size
        self.arrow_color = arrow_color

        self.arrow_head = _ArrowHeadVisual(self)

        # TODO: `LineVisual.__init__` also calls its own `set_data` method,
        # which triggers an *update* event. This results in a redraw. After
        # that we call our own `set_data` method, which triggers another
        # redraw. This should be fixed.
        LineVisual.__init__(self, pos, color, width, connect, method,
                            antialias)
        ArrowVisual.set_data(self, arrows=arrows)

        # Add marker visual for the arrow head
        self.add_subvisual(self.arrow_head)

    def set_data(self, pos=None, color=None, width=None, connect=None,
                 arrows=None):
        """Set the data used for this visual

        Parameters
        ----------
        pos : array
            Array of shape (..., 2) or (..., 3) specifying vertex coordinates.
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
        arrows : array
            A (N, 4) or (N, 6) matrix where each row contains the (x, y) or the
            (x, y, z) coordinate of the first and second vertex of the arrow
            body. Remember that the second vertex is used as center point for
            the arrow head, and the first vertex is only used for determining
            the arrow head orientation.
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
            if value <= 0.0:
                raise ValueError("Arrow size should be greater than zero.")

            self._arrow_size = value

        self._arrows_changed = True

    @property
    def arrow_color(self):
        return self._arrow_color

    @arrow_color.setter
    def arrow_color(self, value):
        if value is not None:
            self._arrow_color = value
            self._arrows_changed = True

    @property
    def arrows(self):
        return self._arrows
