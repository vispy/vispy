# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import math
import numpy as np

from .base_camera import BaseCamera
from ...util import keys
from ...visuals.transforms import MatrixTransform


class PerspectiveCamera(BaseCamera):
    """ Base class for 3D cameras supporting orthographic and
    perspective projections.

    Parameters
    ----------
    fov : float
        Field of view. Default 60.0.
    scale_factor : scalar
        A measure for the scale/range of the scene that the camera
        should show. The exact meaning differs per camera type.
    **kwargs : dict
        Keyword arguments to pass to `BaseCamera`.
    """

    _state_props = ('scale_factor', 'center', 'fov')

    def __init__(self, fov=60.0, scale_factor=None, center=None, **kwargs):
        super(PerspectiveCamera, self).__init__(**kwargs)
        # Camera transform
        self.transform = MatrixTransform()

        # Set camera attributes
        self.fov = fov
        self._scale_factor = None
        self._center = None

        # Only set if they are given. They're set during _set_range if None
        if scale_factor is not None:
            self.scale_factor = scale_factor
        if center is not None:
            self.center = center

    def viewbox_mouse_event(self, event):
        """ The ViewBox received a mouse event; update transform
        accordingly.
        Default implementation adjusts scale factor when scolling.

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        BaseCamera.viewbox_mouse_event(self, event)
        if event.type == 'mouse_wheel':
            s = 1.1 ** - event.delta[1]
            self._scale_factor *= s
            if self._distance is not None:
                self._distance *= s
            self.view_changed()

    @property
    def scale_factor(self):
        """ The measure for the scale or range that the camera should cover

        For the PanZoomCamera and TurnTableCamera this translates to
        zooming: set to smaller values to zoom in.
        """
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, value):
        self._scale_factor = abs(float(value))
        self.view_changed()

    @property
    def near_clip_distance(self):
        """ The distance of the near clipping plane from the camera's position.
        """
        return self._near_clip_distance

    def _set_range(self, init):
        """ Reset the camera view using the known limits.
        """

        if init and (self._scale_factor is not None):
            return  # We don't have to set our scale factor

        # Get window size (and store factor now to sync with resizing)
        w, h = self._viewbox.size
        w, h = float(w), float(h)

        # Get range and translation for x and y
        x1, y1, z1 = self._xlim[0], self._ylim[0], self._zlim[0]
        x2, y2, z2 = self._xlim[1], self._ylim[1], self._zlim[1]
        rx, ry, rz = (x2 - x1), (y2 - y1), (z2 - z1)

        # Correct ranges for window size. Note that the window width
        # influences the x and y data range, while the height influences
        # the z data range.
        if w / h > 1:
            rx /= w / h
            ry /= w / h
        else:
            rz /= h / w

        # Convert to screen coordinates. In screen x, only x and y have effect.
        # In screen y, all three dimensions have effect. The idea of the lines
        # below is to calculate the range on screen when that will fit the
        # data under any rotation.
        rxs = (rx**2 + ry**2)**0.5
        rys = (rx**2 + ry**2 + rz**2)**0.5

        self.scale_factor = max(rxs, rys) * 1.04  # 4% extra space

    def viewbox_resize_event(self, event):
        """The ViewBox resize handler to update the transform

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        self.view_changed()

    def _update_transform(self, event=None):
        # Do we have a viewbox
        if self._viewbox is None:
            return

        # Calculate viewing range for x and y
        fx = fy = self._scale_factor

        # Correct for window size
        w, h = self._viewbox.size
        if w / h > 1:
            fx *= w / h
        else:
            fy *= h / w

        self._update_projection_transform(fx, fy)

        # assemble complete transform mapping to viewbox bounds
        unit = [[-1, 1], [1, -1]]
        vrect = [[0, 0], self._viewbox.size]
        self._viewbox_tr.set_mapping(unit, vrect)
        transforms = [n.transform for n in
                      self._viewbox.scene.node_path_to_child(self)[1:]]
        camera_tr = self._transform_cache.get(transforms).inverse
        full_tr = self._transform_cache.get([self._viewbox_tr,
                                             self._projection,
                                             camera_tr])
        self._transform_cache.roll()
        self._set_scene_transform(full_tr)

    def _update_projection_transform(self, fx, fy):
        d = self.depth_value
        if self._fov == 0:
            self._projection.set_ortho(-0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy, 0, d)
        else:
            fov = max(0.01, self._fov)
            dist = fy / (2 * math.tan(math.radians(fov)/2))
            val = math.sqrt(d)
            self._projection.set_perspective(fov, fx/fy, dist/val, dist*val)


class Base3DRotationCamera(PerspectiveCamera):
    """Base class for TurntableCamera and ArcballCamera"""

    def __init__(self, fov=0.0, **kwargs):
        super(Base3DRotationCamera, self).__init__(fov=fov, **kwargs)
        self._actual_distance = 0.0
        self._event_value = None

    @property
    def distance(self):
        """ The user-set distance. If None (default), the distance is
        internally calculated from the scale factor and fov.
        """
        return self._distance

    @distance.setter
    def distance(self, distance):
        if distance is None:
            self._distance = None
        else:
            self._distance = float(distance)
        self.view_changed()

    def viewbox_mouse_event(self, event):
        """
        The viewbox received a mouse event; update transform
        accordingly.

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        if event.handled or not self.interactive:
            return

        PerspectiveCamera.viewbox_mouse_event(self, event)

        if event.type == 'mouse_release':
            self._event_value = None  # Reset
        elif event.type == 'mouse_press':
            event.handled = True
        elif event.type == 'mouse_move':
            if event.press_event is None:
                return

            modifiers = event.mouse_event.modifiers
            p1 = event.mouse_event.press_event.pos
            p2 = event.mouse_event.pos
            d = p2 - p1

            if 1 in event.buttons and not modifiers:
                # Rotate
                self._update_rotation(event)

            elif 2 in event.buttons and not modifiers:
                # Zoom
                if self._event_value is None:
                    self._event_value = (self._scale_factor, self._distance)
                zoomy = (1 + self.zoom_factor) ** d[1]
                
                self.scale_factor = self._event_value[0] * zoomy
                # Modify distance if its given
                if self._distance is not None:
                    self._distance = self._event_value[1] * zoomy
                self.view_changed()

            elif 1 in event.buttons and keys.SHIFT in modifiers:
                # Translate
                norm = np.mean(self._viewbox.size)
                if self._event_value is None or len(self._event_value) == 2:
                    self._event_value = self.center
                dist = (p1 - p2) / norm * self._scale_factor
                dist[1] *= -1
                # Black magic part 1: turn 2D into 3D translations
                dx, dy, dz = self._dist_to_trans(dist)
                # Black magic part 2: take up-vector and flipping into account
                ff = self._flip_factors
                up, forward, right = self._get_dim_vectors()
                dx, dy, dz = right * dx + forward * dy + up * dz
                dx, dy, dz = ff[0] * dx, ff[1] * dy, dz * ff[2]
                c = self._event_value
                self.center = c[0] + dx, c[1] + dy, c[2] + dz

            elif 2 in event.buttons and keys.SHIFT in modifiers:
                # Change fov
                if self._event_value is None:
                    self._event_value = self._fov
                fov = self._event_value - d[1] / 5.0
                self.fov = min(180.0, max(0.0, fov))

    def _update_camera_pos(self):
        """ Set the camera position and orientation"""

        # transform will be updated several times; do not update camera
        # transform until we are done.
        ch_em = self.events.transform_change
        with ch_em.blocker(self._update_transform):
            tr = self.transform
            tr.reset()

            up, forward, right = self._get_dim_vectors()

            # Create mapping so correct dim is up
            pp1 = np.array([(0, 0, 0), (0, 0, -1), (1, 0, 0), (0, 1, 0)])
            pp2 = np.array([(0, 0, 0), forward, right, up])
            tr.set_mapping(pp1, pp2)

            tr.translate(-self._actual_distance * forward)
            self._rotate_tr()
            tr.scale([1.0/a for a in self._flip_factors])
            tr.translate(np.array(self.center))

    def _get_dim_vectors(self):
        # Specify up and forward vector
        M = {'+z': [(0, 0, +1), (0, 1, 0)],
             '-z': [(0, 0, -1), (0, 1, 0)],
             '+y': [(0, +1, 0), (1, 0, 0)],
             '-y': [(0, -1, 0), (1, 0, 0)],
             '+x': [(+1, 0, 0), (0, 0, 1)],
             '-x': [(-1, 0, 0), (0, 0, 1)],
             }
        up, forward = M[self.up]
        right = np.cross(forward, up)
        return np.array(up), np.array(forward), right

    def _update_projection_transform(self, fx, fy):
        d = self.depth_value
        if self._fov == 0:
            self._projection.set_ortho(-0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy, -d, d)
            self._actual_distance = self._distance or 0.0
        else:
            # Figure distance to center in order to have correct FoV and fy.
            # Use that auto-distance, or the given distance (if not None).
            fov = max(0.01, self._fov)
            dist = fy / (2 * math.tan(math.radians(fov)/2))
            self._actual_distance = dist = self._distance or dist
            val = math.sqrt(d*10)
            self._projection.set_perspective(fov, fx/fy, dist/val, dist*val)
        # Update camera pos, which will use our calculated _distance to offset
        # the camera
        self._update_camera_pos()

    def _update_rotation(self, event):
        """Update rotation parmeters based on mouse movement"""
        raise NotImplementedError

    def _rotate_tr(self):
        """Rotate the transformation matrix based on camera parameters"""
        raise NotImplementedError

    def _dist_to_trans(self, dist):
        """Convert mouse x, y movement into x, y, z translations"""
        raise NotImplementedError
