# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple polygon visual based on MeshVisual and LineVisual
"""

from __future__ import division

import numpy as np

from .visual import CompoundVisual
from .mesh import MeshVisual
from .line import LineVisual
from ..color import Color
from ..geometry import PolygonData
from ..gloo import set_state


class PolygonVisual(CompoundVisual):
    """
    Displays a 2D polygon

    Parameters
    ----------

    pos : array
        Set of vertices defining the polygon.
    color : str | tuple | list of colors
        Fill color of the polygon.
    border_color : str | tuple | list of colors
        Border color of the polygon.
    border_width : int
        Border width in pixels.
    **kwargs : dict
        Keyword arguments to pass to `PolygonVisual`.
    """
    def __init__(self, pos=None, color='black',
                 border_color=None, border_width=1, **kwargs):
        self._mesh = MeshVisual()
        self._border = LineVisual()
        self._pos = pos
        self._color = Color(color)
        self._border_width = border_width
        self._border_color = Color(border_color)

        self._update()
        CompoundVisual.__init__(self, [self._mesh, self._border], **kwargs)
        self._mesh.set_gl_state(polygon_offset_fill=True,
                                polygon_offset=(1, 1), cull_face=False)
        self.freeze()

    def _update(self):
        self.data = PolygonData(vertices=np.array(self._pos, dtype=np.float32))
        if self._pos is None:
            return
        if not self._color.is_blank:
            pts, tris = self.data.triangulate()
            set_state(polygon_offset_fill=False)
            self._mesh.set_data(vertices=pts, faces=tris.astype(np.uint32),
                                color=self._color.rgba)

        if not self._border_color.is_blank:
            # Close border if it is not already.
            border_pos = self._pos
            if np.any(border_pos[0] != border_pos[1]):
                border_pos = np.concatenate([border_pos, border_pos[:1]],
                                            axis=0)
            self._border.set_data(pos=border_pos,
                                  color=self._border_color.rgba,
                                  width=self._border_width,
                                  connect='strip')

            self._border.update()

    @property
    def pos(self):
        """ The vertex position of the polygon.
        """
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self._update()

    @property
    def color(self):
        """ The color of the polygon.
        """
        return self._color

    @color.setter
    def color(self, color):
        self._color = Color(color, clip=True)
        self._update()

    @property
    def border_color(self):
        """ The border color of the polygon.
        """
        return self._border_color

    @border_color.setter
    def border_color(self, border_color):
        self._border_color = Color(border_color)
        self._update()

    @property
    def mesh(self):
        """The vispy.visuals.MeshVisual that is owned by the PolygonVisual.
           It is used to fill in the polygon
        """
        return self._mesh

    @mesh.setter
    def mesh(self, mesh):
        self._mesh = mesh
        self._update()

    @property
    def border(self):
        """The vispy.visuals.LineVisual that is owned by the PolygonVisual.
           It is used to draw the border of the polygon
        """
        return self._border

    @border.setter
    def border(self, border):
        self._border = border
        self._update()
