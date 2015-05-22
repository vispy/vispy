# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple polygon visual based on MeshVisual and LineVisual
"""

from __future__ import division

import numpy as np

from .. import gloo
from .visual import Visual
from .mesh import MeshVisual
from .line import LineVisual
from ..color import Color
from ..geometry import PolygonData


class PolygonVisual(Visual):
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
        super(PolygonVisual, self).__init__(**kwargs)

        self.mesh = MeshVisual()
        self.border = LineVisual()
        self._pos = pos
        self._color = Color(color)
        self._border_width = border_width
        self._border_color = Color(border_color)
        self._update()
        #glopts = kwargs.pop('gl_options', 'translucent')
        #self.set_gl_options(glopts)

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

    def _update(self):
        self.data = PolygonData(vertices=np.array(self._pos, dtype=np.float32))
        if self._pos is None:
            return
        if not self._color.is_blank:
            pts, tris = self.data.triangulate()
            self.mesh.set_data(vertices=pts, faces=tris.astype(np.uint32),
                               color=self._color.rgba)
        if not self._border_color.is_blank:
            # Close border if it is not already.
            border_pos = self._pos
            if np.any(border_pos[0] != border_pos[1]):
                border_pos = np.concatenate([border_pos, border_pos[:1]], 
                                            axis=0)
            self.border.set_data(pos=border_pos,
                                 color=self._border_color.rgba, 
                                 width=self._border_width,
                                 connect='strip')
        self.update()

    def set_gl_options(self, *args, **kwargs):
        self.mesh.set_gl_options(*args, **kwargs)

    def update_gl_options(self, *args, **kwargs):
        self.mesh.update_gl_options(*args, **kwargs)

    def draw(self, transforms):
        """Draw the visual

        Parameters
        ----------
        transforms : instance of TransformSystem
            The transforms to use.
        """
        if self._pos is None:
            return
        if not self._color.is_blank:
            gloo.set_state(polygon_offset_fill=True, 
                           cull_face=False)
            gloo.set_polygon_offset(1, 1)
            self.mesh.draw(transforms)
        if not self._border_color.is_blank:
            self.border.draw(transforms)
