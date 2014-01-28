# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Implementations of our 3D cameras.
"""

from __future__ import division

import math
import numpy as np

from ..base import Camera
from ...util import transforms, logger


class ThreeDCamera(Camera):

    def __init__(self, parent=None):
        Camera.__init__(self, parent)

        self._pos = 200, 200, 200
        self._fov = 45.0

        self._view_az = -10.0  # azimuth
        self._view_el = 30.0  # elevation
        self._view_ro = 0.0  # roll
        self._fov = 0.0  # field of view - if 0, use ortho view

    def on_mouse_move(self, event):

        if not event.is_dragging:
            return

        if 1 in event.buttons:
            # rotate

            # Get (or set) the reference position)
            if hasattr(event.press_event, '_refangles'):
                refangles = event.press_event._refangles
            else:
                refangles = self._view_az, self._view_el, self._view_ro
                event.press_event._refangles = refangles

            # Get the delta position
            startpos = event.press_event.pos
            curpos = event.pos
            dpos = curpos[0] - startpos[0], curpos[1] - startpos[1]

            # get normalized delta values
            sze = 400, 400  # todo: get from viewbox
            d_az = dpos[0] / sze[0]
            d_el = dpos[1] / sze[1]

            # change az and el accordingly
            self._view_az = refangles[0] - d_az * 90.0
            self._view_el = refangles[1] + d_el * 90.0

            # keep within bounds
            while self._view_az < -180:
                self._view_az += 360
            while self._view_az > 180:
                self._view_az -= 360
            if self._view_el < -90:
                self._view_el = -90
            if self._view_el > 90:
                self._view_el = 90
            logger.debug('(Az %s, El %s)' % (self._view_az, self._view_el))

            # Init matrix
            M = np.eye(4)

            # Move camera backwards to account for perspective
            # this should actually be triggered by change in fov.
            transforms.translate(M, 0, 0, self._d)

            # Rotate it
            transforms.rotate(M, self._view_ro, 0, 0, 1)
            transforms.rotate(M, 270 - self._view_el, 1, 0, 0)
            transforms.rotate(M, -self._view_az, 0, 0, 1)

            # Translate it
            transforms.translate(M, *self._pos)

            # Translate it with previous transform
            # This should also work, because position and rotation
            # are stored in different elements of the matrix ...

#             transforms.translate(M, self.transform[-1, 0],
#                                     self.transform[-1, 1],
#                                     self.transform[-1, 2])

            # Apply
            self._transform = M

    def get_projection(self, viewbox):

        w, h = viewbox.resolution

        fov = self._fov
        aspect = 1.0
        fx, fy = 600.0, 600.0  # todo: hard-coded

        # Calculate distance to center in order to have correct FoV and fy.
        if fov == 0:
            M = transforms.ortho(-
                                 0.5 *
                                 fx, 0.5 *
                                 fx, -
                                 0.5 *
                                 fy, 0.5 *
                                 fy, -
                                 10000, 10000)
            self._d = 0
        else:
            d = fy / (2 * math.tan(math.radians(fov) / 2))
            val = math.sqrt(10000)  # math.sqrt(getDepthValue())
            znear, zfar = d / val, d * val
            M = transforms.perspective(fov, aspect, znear, zfar)
            self._d = d
            # transforms.translate(M, 0, 0, d)  # move camera backwards - done
            # in on_mouse_move

        # Translation and rotation is done by our 'transformation' parameter
        return M


class FirstPersonCamera(Camera):

    def __init__(self, parent=None):
        Camera.__init__(self, parent)

        self._pos = 200, 200, 200
        self._fov = 45.0

        # todo: we probably want quaternions here ...
        self._view_az = -10.0  # azimuth
        self._view_el = 30.0  # elevation
        self._view_ro = 0.0  # roll
        self._fov = 0.0  # field of view - if 0, use ortho view

    def update_angles(self):
        """ Temporary method to turn angles into our transform matrix.
        """

        # Init matrix
        M = np.eye(4)

        # Rotate it
        transforms.rotate(M, self._view_ro, 0, 0, 1)
        transforms.rotate(M, 270 - self._view_el, 1, 0, 0)
        transforms.rotate(M, -self._view_az, 0, 0, 1)

        # Translate it
        transforms.translate(M, *self._pos)

        # Apply
        self._transform = M

    def get_projection(self, viewbox):

        w, h = viewbox.resolution

        fov = self._fov
        aspect = 1.0
        fx = fy = 1.0  # todo: hard-coded

        # Calculate distance to center in order to have correct FoV and fy.
        if fov == 0:
            M = transforms.ortho(-0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy,
                                 -10000, 10000)
            self._d = 0
        else:
            d = fy / (2 * math.tan(math.radians(fov) / 2))
            val = math.sqrt(10000)  # math.sqrt(getDepthValue())
            znear, zfar = d / val, d * val
            M = transforms.perspective(fov, aspect, znear, zfar)

        # Translation and rotation is done by our 'transformation' parameter

        return M
