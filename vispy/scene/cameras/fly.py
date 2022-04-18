# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import math
import numpy as np

from ...app import Timer
from ...util.quaternion import Quaternion
from ...util import keys
from .perspective import PerspectiveCamera


class FlyCamera(PerspectiveCamera):
    """The fly camera provides a way to explore 3D data using an
    interaction style that resembles a flight simulator.

    For this camera, the ``scale_factor`` indicates the speed of the
    camera in units per second, and the ``center`` indicates the
    position of the camera.

    Parameters
    ----------
    fov : float
        Field of view. Default 60.0.
    rotation : float | None
        Rotation to use.
    **kwargs : dict
        Keyword arguments to pass to `BaseCamera`.

    Notes
    -----
    Interacting with this camera might need a bit of practice.
    The reaction to key presses can be customized by modifying the
    keymap property.

    Moving:

      * arrow keys, or WASD to move forward, backward, left and right
      * F and C keys move up and down
      * Space bar to brake

    Viewing:

      * Use the mouse while holding down LMB to control the pitch and yaw.
      * Alternatively, the pitch and yaw can be changed using the keys
        IKJL
      * The camera auto-rotates to make the bottom point down, manual
        rolling can be performed using Q and E.

    """

    # Using _rotation1 and _rotation2 for camera states instead of _rotation
    _state_props = PerspectiveCamera._state_props + ('rotation1', 'rotation2')

    def __init__(self, fov=60, rotation=None, **kwargs):

        # Motion speed vector
        self._speed = np.zeros((6,), 'float64')
        self._distance = None

        # Acceleration and braking vectors, set from keyboard
        self._brake = np.zeros((6,), 'uint8')  # bool-ish
        self._acc = np.zeros((6,), 'float64')

        # Init rotations
        self._auto_roll = True  # Whether to roll to make Z up
        self._rotation1 = Quaternion()  # The base rotation
        self._rotation2 = Quaternion()  # The delta yaw and pitch rotation

        PerspectiveCamera.__init__(self, fov=fov, **kwargs)

        # Set camera attributes
        self.rotation1 = rotation.normalize() if (rotation is not None) else Quaternion()

        # To store data at start of interaction
        self._event_value = None

        # Whether the mouse-system wants a transform update
        self._update_from_mouse = False

        # Mapping that defines keys to thrusters
        self._keymap = {
            keys.UP: (+1, 1), keys.DOWN: (-1, 1),
            keys.RIGHT: (+1, 2), keys.LEFT: (-1, 2),
            #
            'W': (+1, 1), 'S': (-1, 1),
            'D': (+1, 2), 'A': (-1, 2),
            'F': (+1, 3), 'C': (-1, 3),
            #
            'I': (+1, 4), 'K': (-1, 4),
            'L': (+1, 5), 'J': (-1, 5),
            'Q': (+1, 6), 'E': (-1, 6),
            #
            keys.SPACE: (0, 1, 2, 3),  # 0 means brake, apply to translation
            # keys.ALT: (+5, 1),  # Turbo
        }

        # Timer. Each tick we calculate new speed and new position
        self._timer = Timer(0.01, start=False, connect=self.on_timer)

    @property
    def rotation(self):
        """Get the full rotation. This rotation is composed of the
        normal rotation plus the extra rotation due to the current
        interaction of the user.
        """
        rotation = self._rotation2 * self._rotation1
        return rotation.normalize()

    @rotation.setter
    def rotation(self, value):
        print("rotation.setter called, use rotation1.setter instead")

    @property
    def rotation1(self):
        """rotation1 records confirmed camera rotation"""
        return self._rotation1

    @rotation1.setter
    def rotation1(self, value):
        assert isinstance(value, Quaternion)
        self._rotation1 = value.normalize()

    @property
    def rotation2(self):
        """rotation2 records on going camera rotation."""
        return self._rotation2

    @rotation2.setter
    def rotation2(self, value):
        assert isinstance(value, Quaternion)
        self._rotation2 = value.normalize()

    @property
    def auto_roll(self):
        """Whether to rotate the camera automaticall to try and attempt
        to keep Z up.
        """
        return self._auto_roll

    @auto_roll.setter
    def auto_roll(self, value):
        self._auto_roll = bool(value)

    @property
    def keymap(self):
        """A dictionary that maps keys to thruster directions

        The keys in this dictionary are vispy key descriptions (from
        vispy.keys) or characters that represent keys. These are matched
        to the "key" attribute of key-press and key-release events.

        The values are tuples, in which the first element specifies the
        magnitude of the acceleration, using negative values for
        "backward" thrust. A value of zero means to brake. The remaining
        elements specify the dimension to which the acceleration should
        be applied. These are 1, 2, 3 for forward/backward, left/right,
        up/down, and 4, 5, 6 for pitch, yaw, roll.
        """
        return self._keymap

    def _set_range(self, init):
        """Reset the view."""
        # PerspectiveCamera._set_range(self, init)
        # Stop moving
        self._speed *= 0.0

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

        # Do not convert to screen coordinates. This camera does not need
        # to fit everything on screen, but we need to estimate the scale
        # of the data in the scene.

        # Set scale, depending on data range. Initial speed is such that
        # the scene can be traversed in about three seconds.
        self._scale_factor = max(rx, ry, rz) / 3.0

        # Set initial position to a corner of the scene
        margin = np.mean([rx, ry, rz]) * 0.1
        self._center = x1 - margin, y1 - margin, z1 + margin

        # Determine initial view direction based on flip axis
        yaw = 45 * self._flip_factors[0]
        pitch = -90 - 20 * self._flip_factors[2]
        if self._flip_factors[1] < 0:
            yaw += 90 * np.sign(self._flip_factors[0])

        # Set orientation
        q1 = Quaternion.create_from_axis_angle(pitch*math.pi/180, 1, 0, 0)
        q2 = Quaternion.create_from_axis_angle(0*math.pi/180, 0, 1, 0)
        q3 = Quaternion.create_from_axis_angle(yaw*math.pi/180, 0, 0, 1)
        #
        self._rotation1 = (q1 * q2 * q3).normalize()
        self._rotation2 = Quaternion()

        # Update
        self.view_changed()

    def _get_directions(self):

        # Get reference points in reference coordinates
        # p0 = Point(0,0,0)
        pf = (0, 0, -1)  # front
        pr = (1, 0, 0)  # right
        pl = (-1, 0, 0)  # left
        pu = (0, 1, 0)  # up

        # Get total rotation
        rotation = self.rotation.inverse()

        # Transform to real coordinates
        pf = rotation.rotate_point(pf)
        pr = rotation.rotate_point(pr)
        pl = rotation.rotate_point(pl)
        pu = rotation.rotate_point(pu)

        def _normalize(p):
            L = sum(x**2 for x in p) ** 0.5
            return np.array(p, 'float64') / L

        pf = _normalize(pf)
        pr = _normalize(pr)
        pl = _normalize(pl)
        pu = _normalize(pu)

        return pf, pr, pl, pu

    def on_timer(self, event):
        """Timer event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        # Set relative speed and acceleration
        rel_speed = event.dt
        rel_acc = 0.1

        # Get what's forward
        pf, pr, pl, pu = self._get_directions()

        # Increase speed through acceleration
        # Note that self._speed is relative. We can balance rel_acc and
        # rel_speed to get a nice smooth or direct control
        self._speed += self._acc * rel_acc

        # Reduce speed. Simulate resistance. Using brakes slows down faster.
        # Note that the way that we reduce speed, allows for higher
        # speeds if keys ar bound to higher acc values (i.e. turbo)
        reduce = np.array([0.05, 0.05, 0.05, 0.1, 0.1, 0.1])
        reduce[self._brake > 0] = 0.2
        self._speed -= self._speed * reduce
        if np.abs(self._speed).max() < 0.05:
            self._speed *= 0.0

        # --- Determine new position from translation speed

        if self._speed[:3].any():

            # Create speed vectors, use scale_factor as a reference
            dv = np.array([1.0/d for d in self._flip_factors])
            #
            vf = pf * dv * rel_speed * self._scale_factor
            vr = pr * dv * rel_speed * self._scale_factor
            vu = pu * dv * rel_speed * self._scale_factor
            direction = vf, vr, vu

            # Set position
            center_loc = np.array(self._center, dtype='float32')
            center_loc += (self._speed[0] * direction[0] +
                           self._speed[1] * direction[1] +
                           self._speed[2] * direction[2])
            self._center = tuple(center_loc)

        # --- Determine new orientation from rotation speed

        roll_angle = 0

        # Calculate manual roll (from speed)
        if self._speed[3:].any():
            angleGain = np.array([1.0, 1.5, 1.0]) * 3 * math.pi / 180
            angles = self._speed[3:] * angleGain

            q1 = Quaternion.create_from_axis_angle(angles[0], -1, 0, 0)
            q2 = Quaternion.create_from_axis_angle(angles[1], 0, 1, 0)
            q3 = Quaternion.create_from_axis_angle(angles[2], 0, 0, -1)
            q = q1 * q2 * q3
            self._rotation1 = (q * self._rotation1).normalize()

        # Calculate auto-roll
        if self.auto_roll:
            up = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[self.up[1]]
            up = np.array(up) * {'+': +1, '-': -1}[self.up[0]]

            def angle(p1, p2):
                return np.arccos(p1.dot(p2))
            # au = angle(pu, (0, 0, 1))
            ar = angle(pr, up)
            al = angle(pl, up)
            af = angle(pf, up)
            # Roll angle that's off from being leveled (in unit strength)
            roll_angle = math.sin(0.5*(al - ar))
            # Correct for pitch
            roll_angle *= abs(math.sin(af))  # abs(math.sin(au))
            if abs(roll_angle) < 0.05:
                roll_angle = 0
            if roll_angle:
                # Correct to soften the force at 90 degree angle
                roll_angle = np.sign(roll_angle) * np.abs(roll_angle)**0.5
                # Get correction for this iteration and apply
                angle_correction = 1.0 * roll_angle * math.pi / 180
                q = Quaternion.create_from_axis_angle(angle_correction,
                                                      0, 0, 1)
                self._rotation1 = (q * self._rotation1).normalize()

        # Update
        if self._speed.any() or roll_angle or self._update_from_mouse:
            self._update_from_mouse = False
            self.view_changed()

    def viewbox_key_event(self, event):
        """The ViewBox key event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        PerspectiveCamera.viewbox_key_event(self, event)

        if event.handled or not self.interactive:
            return

        # Ensure the timer runs
        if not self._timer.running:
            self._timer.start()

        if event.key in self._keymap:
            val_dims = self._keymap[event.key]
            val = val_dims[0]
            # Brake or accelarate?
            if val == 0:
                vec = self._brake
                val = 1
            else:
                vec = self._acc
            # Set
            if event.type == 'key_release':
                val = 0
            for dim in val_dims[1:]:
                factor = 1.0
                vec[dim-1] = val * factor
            event.handled = True

    def viewbox_mouse_event(self, event):
        """The ViewBox mouse event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        PerspectiveCamera.viewbox_mouse_event(self, event)

        if event.handled or not self.interactive:
            return

        if event.type == 'mouse_wheel':
            if not event.mouse_event.modifiers:
                # Move forward / backward
                self._speed[0] += 0.5 * event.delta[1]
            elif keys.SHIFT in event.mouse_event.modifiers:
                # Speed
                s = 1.1 ** - event.delta[1]
                self.scale_factor /= s  # divide instead of multiply
                print('scale factor: %1.1f units/s' % self.scale_factor)
            return

        if event.type == 'mouse_press':
            event.handled = True

        if event.type == 'mouse_release':
            # Reset
            self._event_value = None
            # Apply rotation
            self._rotation1 = (self._rotation2 * self._rotation1).normalize()
            self._rotation2 = Quaternion()
            event.handled = True
        elif not self._timer.running:
            # Ensure the timer runs
            self._timer.start()

        if event.type == 'mouse_move':

            if event.press_event is None:
                return
            if not event.buttons:
                return

            # Prepare
            modifiers = event.mouse_event.modifiers
            pos1 = event.mouse_event.press_event.pos
            pos2 = event.mouse_event.pos
            w, h = self._viewbox.size

            if 1 in event.buttons and not modifiers:
                # rotate

                # get normalized delta values
                d_az = -float(pos2[0] - pos1[0]) / w
                d_el = +float(pos2[1] - pos1[1]) / h
                # Apply gain
                d_az *= - 0.5 * math.pi  # * self._speed_rot
                d_el *= + 0.5 * math.pi  # * self._speed_rot
                # Create temporary quaternions
                q_az = Quaternion.create_from_axis_angle(d_az, 0, 1, 0)
                q_el = Quaternion.create_from_axis_angle(d_el, 1, 0, 0)

                # Apply to global quaternion
                self._rotation2 = (q_el.normalize() * q_az).normalize()
                event.handled = True

            elif 2 in event.buttons and keys.CONTROL in modifiers:
                # zoom --> fov
                if self._event_value is None:
                    self._event_value = self._fov
                p1 = np.array(event.press_event.pos)[:2]
                p2 = np.array(event.pos)[:2]
                p1c = event.map_to_canvas(p1)[:2]
                p2c = event.map_to_canvas(p2)[:2]
                d = p2c - p1c
                fov = self._event_value * math.exp(-0.01*d[1])
                self._fov = min(90.0, max(10, fov))
                event.handled = True

        # Make transform be updated on the next timer tick.
        # By doing it at timer tick, we avoid shaky behavior
        self._update_from_mouse = True

    def _update_projection_transform(self, fx, fy):
        PerspectiveCamera._update_projection_transform(self, fx, fy)

        # Turn our internal quaternion representation into rotation
        # of our transform

        axis_angle = self.rotation.get_axis_angle()
        angle = axis_angle[0] * 180 / math.pi

        tr = self.transform
        tr.reset()
        #
        tr.rotate(-angle, axis_angle[1:])
        tr.scale([1.0/a for a in self._flip_factors])
        tr.translate(self._center)
