# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""RegularPolygonVisual visual based on EllipseVisual"""

from __future__ import division

from .ellipse import EllipseVisual


class RegularPolygonVisual(EllipseVisual):
    """
    Displays a regular polygon

    Parameters
    ----------
    center : array-like (x, y)
        Center of the regular polygon
    color : str | tuple | list of colors
        Fill color of the polygon
    border_color : str | tuple | list of colors
        Border color of the polygon
    border_width: float
        The width of the border in pixels
    radius : float
        Radius of the regular polygon
        Defaults to  0.1
    sides : int
        Number of sides of the regular polygon
    """

    def __init__(self, center=None, color='black', border_color=None,
                 border_width=1, radius=0.1, sides=4, **kwargs):
        EllipseVisual.__init__(self, center=center,
                               radius=radius,
                               color=color,
                               border_color=border_color,
                               border_width=border_width,
                               num_segments=sides, **kwargs)

    @property
    def sides(self):
        """The number of sides in the regular polygon."""
        # return using the property accessor for num_segments
        return self.num_segments

    @sides.setter
    def sides(self, sides):
        if sides < 3:
            raise ValueError('PolygonVisual must have at least 3 sides, not %s'
                             % sides)
        # edit using the property accessor of num_segments so this
        # internally calls the update()
        self.num_segments = sides
