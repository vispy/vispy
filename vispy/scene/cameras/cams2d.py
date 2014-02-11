# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Implementations of our 2D cameras.
"""

from __future__ import division

import numpy as np

from ..base import Camera
from ...util import transforms


class NDCCamera(Camera):

    """ Camera that presents a view on the world in normalized device
    coordinates (-1..1).
    """
    pass


class PixelCamera(Camera):

    """ Camera that presents a view on the world in pixel coordinates.
    The coordinates map directly to the viewbox coordinates. The origin
    is in the upper left.
    """

    def get_projection(self, viewbox):
        w, h = viewbox.resolution
        projection = np.eye(4)
        transforms.scale(projection, 2.0 / w, 2.0 / h)
        transforms.translate(projection, -1, -1)
        transforms.scale(projection, 1, -1)  # Flip y-axis
        return projection


class TwoDCamera(Camera):

    def __init__(self, parent=None):
        Camera.__init__(self, parent)
        self.fov = 1, 1

    # xlim and ylim are convenience methods to set the view using limits
    @property
    def xlim(self):
        x = self.transform[-1, 0]
        dx = self.fov[0] / 2.0
        return x - dx, x + dx

    @property
    def ylim(self):
        y = self.transform[-1, 1]
        dy = self.fov[1] / 2.0
        return y - dy, y + dy

    @xlim.setter
    def xlim(self, value):
        x = 0.5 * (value[0] + value[1])
        rx = max(value) - min(value)
        self.fov = rx, self.fov[1]
        self.transform[-1, 0] = x

    @ylim.setter
    def ylim(self, value):
        y = 0.5 * (value[0] + value[1])
        ry = max(value) - min(value)
        self.fov = self.fov[0], ry
        self.transform[-1, 1] = y

    def get_projection(self, viewbox):
        w, h = self.fov
        projection = np.eye(4)
        transforms.scale(projection, 2.0 / w, 2.0 / h)
        transforms.scale(projection, 1, -1)  # Flip y-axis
        return projection

    def on_mouse_press(self, event):
        pass

    def on_mouse_move(self, event):
        if event.is_dragging:

            # Get (or set) the reference position)
            if hasattr(event.press_event, 'reflim'):
                pos, fov = event.press_event.reflim
            else:
                pos = self.transform[-1, 0], self.transform[-1, 1]
                pos, fov = event.press_event.reflim = pos, self.fov

            # Get the delta position
            startpos = event.press_event.pos
            curpos = event.pos
            dpos = curpos[0] - startpos[0], curpos[1] - startpos[1]

            if 1 in event.buttons:
                # Pan
                self.transform[-1, 0] = pos[0] - dpos[0] / 2
                self.transform[-1, 1] = pos[1] - dpos[1] / 2
                #dx, dy = -dpos[0] / 2, -dpos[1] / 2
                #self.xlim = xlim[0]+dx, xlim[1]+dx
                #self.ylim = ylim[0]+dy, ylim[1]+dy
            elif 2 in event.buttons:
                # Zoom
                self.fov = (fov[0] - dpos[0] / 2,
                            fov[1] + dpos[1] / 2)
                #dx, dy = -dpos[0] / 2, dpos[1] / 2
                #self.xlim = xlim[0]-dx, xlim[1]+dx
                #self.ylim = ylim[0]-dy, ylim[1]+dy

            # Force redraw
            event.source.update()
