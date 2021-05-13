#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# 2016, Scott Paine
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------

"""
**********
Wiggly Bar
**********
Usage of VisPy to numerically simulate and view a simple physics model.

.. image:: http://i.imgur.com/ad0s9lB.png

This is a simple example of using VisPy to simulate a system with
two springs, a pivot, and a mass.

The system evolves in a nonlinear fashion, according to two equations:

.. image:: http://i.imgur.com/8reci4N.png

In these equations, the J term is the polar moment of inertia of the rod
given by:

.. image:: http://i.imgur.com/94cI1TL.png

The system has the option to update once every step using the
`Euler <https://en.wikipedia.org/wiki/Euler_method>`_ method
or a more stable third-order
`Runge-Kutta <https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods>`_
method. The instability of the Euler Method becomes apparent as the time step
is increased.
"""

from __future__ import division, print_function, absolute_import
from vispy import app, visuals
from vispy.visuals import transforms
from vispy.io import load_data_file
import sys
import numpy as np
import string
import logging
import traceback

# To switch between PyQt5 and PySide2 bindings just change the from import
from PyQt5 import QtCore, QtGui, QtWidgets
# Provide automatic signal function selection for PyQt5/PySide2
pyqtsignal = QtCore.pyqtSignal if hasattr(QtCore, 'pyqtSignal') else QtCore.Signal

logger = logging.getLogger(__name__)

VALID_METHODS = ['euler', 'runge-kutta']

PARAMETERS = [('d1', 0.0, 10.0, 'double', 0.97),
              ('d2', 0.0, 10.0, 'double', 0.55),
              ('m', 0.01, 100.0, 'double', 2.0),
              ('M', 0.01, 100.0, 'double', 12.5),
              ('k1', 0.01, 75.0, 'double', 1.35),
              ('k2', 0.01, 75.0, 'double', 0.50),
              ('b', 1.0, 1000.0, 'double', 25.75),
              ('time step', 0.001, 1.0, 'double', 1/60),
              ('x', -0.25, 0.25, 'double', -0.01),
              ('x dot', -10.0, 10.0, 'double', -0.12),
              ('theta', -np.pi/5, np.pi/5, 'double', 0.005),
              ('theta dot', -np.pi/2, np.pi/2, 'double', 0.0),
              ('scale', 5, 500, 'int', 50),
              ('font size', 6.0, 128.0, 'double', 24.0)]

CONVERSION_DICT = {'d1': 'd1', 'd2': 'd2', 'm': 'little_m', 'M': 'big_m',
                   'k1': 'spring_k1', 'k2': 'spring_k2', 'b': 'b',
                   'x': 'x', 'x dot': 'x_dot', 'theta': 'theta', 
                   'theta dot': 'theta_dot', 'scale': 'scale',
                   'time step': 'dt', 'font size': 'font_size'}


def make_spiral(num_points=100, num_turns=4, height=12, radius=2.0,
                xnot=None, ynot=None, znot=None):
    """
    Generate a list of points corresponding to a spiral.

    Parameters
    ----------
    num_points : int
        Number of points to map spiral over. More points means a
        rounder spring.
    num_turns : int
        Number of coils in the spiral
    height : float
        The height of the spiral. Keep it in whatever units the rest of the 
        spiral is in.
    radius : float
        The radius of the coils. The spiral will end up being 2*radius wide.
    xnot : float
        Initial x-coordinate for the spiral coordinates to start at.
    ynot : float
        Initial y-coordinate for the spiral coordinates to start at.
    znot : float
        Initial z-coordinate for the spiral coordinates to start at.

    Returns
    -------
    coord_list: list of tuples
        Coordinate list of (x, y, z) positions for the spiral

    Notes
    -----
    Right now, this assumes the center is at x=0, y=0. Later, it might be 
    good to add in stuff to change that.

    """

    coords_list = []
    znot = -4 if znot is None else znot
    xnot = radius if xnot is None else xnot
    ynot = 0 if ynot is None else ynot

    theta_not = np.arctan2(ynot, xnot)

    coords_list.append((xnot, ynot, znot))

    for point in range(num_points):
        znot += height / num_points
        theta_not += 2 * np.pi * num_turns / num_points
        xnot = np.cos(theta_not) * radius
        ynot = np.sin(theta_not) * radius
        coords_list.append((xnot, ynot, znot))
    return coords_list


def make_spring(num_points=300, num_turns=4, height=12, radius=2.0,
                xnot=None, ynot=None, znot=None):
    """
        Generate a list of points corresponding to a spring.

        Parameters
        ----------
        num_points : int
            Number of points to map spring over. More points means a rounder 
            spring.
        num_turns : int
            Number of coils in the spring
        height : float
            The height of the spring. Keep it in whatever units the rest of the 
            spring is in.
        radius : float
            The radius of the coils. The spring will end up being
            2*radius wide.
        xnot : float
            Initial x-coordinate for the spring coordinates to start at.
        ynot : float
            Initial y-coordinate for the spring coordinates to start at.
        znot : float
            Initial z-coordinate for the spring coordinates to start at.

        Returns
        -------
        coord_list: list of tuples
            Coordinate list of (x, y, z) positions for the spring

        Notes
        -----
        Right now, this assumes the center is at x=0, y=0. Later, it might be 
        good to add in stuff to change that.

        Right now, the length of the "ends" is 10% of the overall length, as 
        well as a small "turn" that is length radius / 2. In the future, maybe 
        there could be a kwarg to set the length of the sides of the spring. 
        For now, 10% looks good.

        """
    coords_list = []
    init_pts = num_points // 10
    znot = 0 if znot is None else znot
    xnot = 0 if xnot is None else xnot
    ynot = 0 if ynot is None else ynot
    coords_list.append((xnot, ynot, znot))
    for _ in range(init_pts):
        znot += height / num_points
        coords_list.append((xnot, ynot, znot))
    hold_z = znot
    for i in range(init_pts // 2):
        small_theta = (i + 1) * np.pi / init_pts
        xnot = radius / 2 * (1 - np.cos(small_theta))
        znot = hold_z + radius / 2 * np.sin(small_theta)
        coords_list.append((xnot, ynot, znot))
    coords_list += make_spiral(num_points=num_points - 3 * init_pts,
                               num_turns=num_turns,
                               height=(
                                   height - 
                                   (91 * height / num_points) - 
                                   radius / 2
                               ),
                               radius=radius,
                               xnot=xnot,
                               ynot=ynot,
                               znot=znot)
    hold_z = coords_list[-1][-1]
    for i in range(init_pts // 2):
        small_theta = np.pi / 2 - (i + 1) * np.pi / init_pts
        xnot = radius / 2 * (1 - np.cos(small_theta))
        znot = hold_z + radius / 2 * np.cos(small_theta)
        coords_list.append((xnot, ynot, znot))
    xnot = 0.0
    znot += height / num_points
    for _ in range(init_pts):
        znot += height / num_points
        coords_list.append((xnot, ynot, znot))
    coords_list.append((0, 0, height))

    return coords_list


class WigglyBar(app.Canvas):
    def __init__(self, d1=None, d2=None, little_m=None, big_m=None,
                 spring_k1=None, spring_k2=None, b=None,
                 x=None, x_dot=None, theta=None, theta_dot=None,
                 px_len=None, scale=None, pivot=False, method='Euler', dt=None, 
                 font_size=None):
        """
        Main VisPy Canvas for simulation of physical system.

        Parameters
        ----------
        d1 : float
            Length of rod (in meters) from pivot to upper spring.
        d2 : float
            Length of rod (in meters) from pivot to lower spring.
        little_m : float
            Mass of attached cube (in kilograms).
        big_m : float
            Mass of rod (in kilograms).
        spring_k1 : float
            Spring constant of lower spring (in N/m).
        spring_k2 : float
            Spring constant of upper spring (in N/m).
        b : float
            Coefficient of quadratic sliding friction (in kg/m).
        x : float
            Initial x-position of mass (in m).
        x_dot : float
            Initial x-velocity of mass (in m/s).
        theta : float
            Initial angle of rod, with respect to vertical (in radians).
        theta_dot : float
            Initial angular velocity of rod (in rad/s).
        px_len : int
            Length of the rod, in pixels.
        scale : int
            Scaling factor to change size of elements.
        pivot : bool
            Switch for showing/hiding pivot point.
        method : str
            Method to use for updating.
        dt : float
            Time step for simulation.
        font_size : float
            Size of font for text elements, in points.

        Notes
        -----

        As of right now, the only supported methods are "euler" or
        "runge-kutta". These correspond to an Euler method or an
        order 3 Runge-Kutta method for updating x, theta, x dot, and theta dot.

        """

        app.Canvas.__init__(self, title='Wiggly Bar', size=(800, 800),
                            create_native=False)

        # Some initialization constants that won't change
        self.standard_length = 0.97 + 0.55
        self.center = np.asarray((500, 450))
        self.visuals = []

        self._set_up_system(
            d1=d1, d2=d2, little_m=little_m, big_m=big_m,
            spring_k1=spring_k1, spring_k2=spring_k2, b=b,
            x=x, x_dot=x_dot, theta=theta, theta_dot=theta_dot,
            px_len=px_len, scale=scale, pivot=pivot, method=method,
            dt=dt, font_size=font_size
        )

        piv_x_y_px = np.asarray((
            self.pivot_loc_px * np.sin(self.theta),
            -1 * self.pivot_loc_px * (np.cos(self.theta))
        ))

        # Make the spring points
        points = make_spring(height=self.px_len/4, radius=self.px_len/24)

        # Put up a text visual to display time info
        self.font_size = 24. if font_size is None else font_size
        self.text = visuals.TextVisual('0:00.00',
                                       color='white',
                                       pos=[50, 250, 0],
                                       anchor_x='left',
                                       anchor_y='bottom')
        self.text.font_size = self.font_size

        # Let's put in more text so we know what method is being used to 
        # update this
        self.method_text = visuals.TextVisual(
            'Method: {}'.format(self.method),
            color='white',
            pos=[50, 250, 0],
            anchor_x='left',
            anchor_y='top'
        )
        self.method_text.font_size = 2/3 * self.font_size

        # Get the pivoting bar ready
        self.rod = visuals.BoxVisual(width=self.px_len/40,
                                     height=self.px_len/40,
                                     depth=self.px_len,
                                     color='white')
        self.rod.transform = transforms.MatrixTransform()
        self.rod.transform.scale(
            (self.scale, self.scale * self.rod_scale, 0.0001)
        )
        self.rod.transform.rotate(np.rad2deg(self.theta), (0, 0, 1))
        self.rod.transform.translate(self.center - piv_x_y_px)

        # Show the pivot point (optional)
        pivot_center = (self.center[0], self.center[1], -self.px_len/75)
        self.center_point = visuals.SphereVisual(radius=self.px_len/75,
                                                 color='red')
        self.center_point.transform = transforms.MatrixTransform()
        self.center_point.transform.scale((self.scale, self.scale, 0.0001))
        self.center_point.transform.translate(pivot_center)

        # Get the upper spring ready.
        self.spring_2 = visuals.TubeVisual(
            points, radius=self.px_len/100, color=(0.5, 0.5, 1, 1)
        )
        self.spring_2.transform = transforms.MatrixTransform()
        self.spring_2.transform.rotate(90, (0, 1, 0))
        self.spring_2.transform.scale((self.scale, self.scale, 0.0001))
        self.spring_2.transform.translate(self.center + self.s2_loc)

        # Get the lower spring ready.
        self.spring_1 = visuals.TubeVisual(
            points, radius=self.px_len/100, color=(0.5, 0.5, 1, 1)
        )
        self.spring_1.transform = transforms.MatrixTransform()
        self.spring_1.transform.rotate(90, (0, 1, 0))
        self.spring_1.transform.scale(
            (
                self.scale *
                (1.0-(self.x*self.px_per_m)/(self.scale*self.px_len/2)),
                self.scale,
                0.0001
            )
        )
        self.spring_1.transform.translate(self.center + self.s1_loc)

        # Finally, prepare the mass that is being moved
        self.mass = visuals.BoxVisual(
            width=self.px_len / 4, height=self.px_len / 8,
            depth=self.px_len / 4, color='white'
        )
        self.mass.transform = transforms.MatrixTransform()
        self.mass.transform.scale((self.scale, self.scale, 0.0001))
        self.mass.transform.translate(self.center + self.mass_loc)

        # Append all the visuals
        self.visuals.append(self.center_point)
        self.visuals.append(self.rod)
        self.visuals.append(self.spring_2)
        self.visuals.append(self.spring_1)
        self.visuals.append(self.mass)
        self.visuals.append(self.text)
        self.visuals.append(self.method_text)

        # Set up a timer to update the image and give a real-time rendering
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

    def on_draw(self, ev):
        # Stolen from previous - just clears the screen and redraws stuff
        self.context.set_clear_color((0, 0, 0, 1))
        self.context.set_viewport(0, 0, *self.physical_size)
        self.context.clear()
        for vis in self.visuals:
            if vis is self.center_point and not self.show_pivot:
                continue
            else:
                vis.draw()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)

        for vis in self.visuals:
            vis.transforms.configure(canvas=self, viewport=vp)

    def on_timer(self, ev):
        # Update x, theta, x_dot, theta_dot
        self.params_update(dt=self.dt, method=self.method)

        # Calculate change for the upper spring, relative to its starting point
        extra_term = self.theta - self.theta_not
        trig_junk = (
            np.sin(self.theta_not) * (np.cos(extra_term) - 1) +
            np.cos(self.theta_not) * np.sin(extra_term)
        )
        delta_x = self.d1 * self.px_per_m * trig_junk
        net_s2_scale = (1 - (delta_x / (self.scale * self.px_len / 4)))

        # Calculate change for the lower spring, relative to something 
        # arbitrary so I didn't have horrors mathematically
        trig_junk_2 = np.sin(self.theta_not) - np.sin(self.theta)
        first_term = self.d2 * trig_junk_2
        top_term = (first_term - self.x)*self.px_per_m
        net_s1_scale = 1 + top_term/self.s1_l_not
        self.s1_loc[0] = -0.5 * (
            -self.x*self.px_per_m + 
            self.s1_l_not +
            self.d2*self.px_per_m*(np.sin(self.theta)+np.sin(self.theta_not))
        )
        self.s1_loc[0] -= 0.5 * net_s1_scale * self.s1_l_not

        # Calculate the new pivot location - this is important because the 
        # rotation occurs about
        # the center of the rod, so it has to be offset appropriately
        piv_x_y_px = np.asarray((
            self.pivot_loc_px*np.sin(self.theta),
            -1 * self.pivot_loc_px*np.cos(self.theta)
        ))

        # Calculate the new mass x location, relative (again) to some 
        # simple parameter where x=0
        self.mass_loc[0] = self.x_is_0 + self.x * self.px_per_m

        # Figure out how much time has passed
        millis_passed = int(100 * (self.t % 1))
        sec_passed = int(self.t % 60)
        min_passed = int(self.t // 60)

        # Apply the necessary transformations to the rod
        self.rod.transform.reset()
        self.rod.transform.scale(
            (self.scale, self.scale * self.rod_scale, 0.0001)
        )
        self.rod.transform.rotate(np.rad2deg(self.theta), (0, 0, 1))
        self.rod.transform.translate(self.center - piv_x_y_px)

        # Redraw and rescale the upper spring
        self.spring_2.transform.reset()
        self.spring_2.transform.rotate(90, (0, 1, 0))
        self.spring_2.transform.scale((net_s2_scale * self.scale,
                                       self.scale,
                                       0.0001))
        self.spring_2.transform.translate(self.center +
                                          self.s2_loc +
                                          np.asarray([delta_x, 0]))

        # Redraw and rescale the lower spring
        # (the hardest part to get, mathematically)
        self.spring_1.transform.reset()
        self.spring_1.transform.rotate(90, (0, 1, 0))
        self.spring_1.transform.scale((net_s1_scale * self.scale,
                                       self.scale,
                                       0.0001))
        self.spring_1.transform.translate(self.center +
                                          self.s1_loc)

        # Redrew and rescale the mass
        self.mass.transform.reset()
        self.mass.transform.scale((self.scale, self.scale, 0.0001))
        self.mass.transform.translate(self.center + self.mass_loc)

        # Update the timer with how long it's been
        self.text.text = '{:0>2d}:{:0>2d}.{:0>2d}'.format(min_passed,
                                                          sec_passed,
                                                          millis_passed)

        # Trigger all of the drawing and updating
        self.update()

    def params_update(self, dt, method='euler'):
        # Uses either Euler method or Runge-Kutta, 
        # depending on your input to "method"

        if method.lower() == 'euler':
            self._euler_update(dt)
        elif method.lower() == 'runge-kutta':
            self._runge_kutta_update(dt)

    def _euler_update(self, dt):
        """Update system using Euler's method (equivalent to order 1
        Runge-Kutta Method).
        """
        # Calculate the second derivative of x
        x_dd_t1 = -self.b * self.x_dot * np.abs(self.x_dot)
        x_dd_t2 = -self.spring_k1 * (self.x + self.d2 * self.theta)
        x_dot_dot = (x_dd_t1 + x_dd_t2) / self.little_m

        # Calculate the second derivative of theta
        term1 = -self.spring_k1 * self.d2 * self.x
        term2 = (
            -self.theta * 
            (self.spring_k1*(self.d2**2) + self.spring_k2*(self.d1**2))
        )
        theta_dot_dot = (term1 + term2) / self.j_term

        # Update everything appropriately
        self.t += dt
        self.x += dt * self.x_dot
        self.theta += dt * self.theta_dot
        self.x_dot += dt * x_dot_dot
        self.theta_dot += dt * theta_dot_dot

    def _runge_kutta_update(self, dt):
        """Update using order 3 Runge-Kutta Method.
        """
        info_vector = np.asarray(
            [self.x_dot, self.theta_dot, self.x, self.theta]
        ).copy()

        t1a = -self.b * info_vector[0] * np.abs(info_vector[0])
        t1b = -self.spring_k1*(info_vector[2] + self.d2*info_vector[3])

        t2a = -self.spring_k1*self.d2*info_vector[2]
        t2b = -info_vector[3] * (
            self.spring_k1*(self.d2 ** 2) + self.spring_k2*(self.d1 ** 2)
        )

        k1 = [
            (t1a + t1b)/self.little_m,
            (t2a + t2b)/self.j_term,
            info_vector[0],
            info_vector[1]
        ]

        k1 = np.asarray(k1) * dt

        updated_est = info_vector + 0.5 * k1

        t1a = -self.b * updated_est[0] * np.abs(updated_est[0])
        t1b = -self.spring_k1 * (updated_est[2] + self.d2 * updated_est[3])

        t2a = -self.spring_k1 * self.d2 * updated_est[2]
        t2b = -updated_est[3] * (
            self.spring_k1 * (self.d2 ** 2) + self.spring_k2 * (self.d1 ** 2)
        )

        k2 = [
            (t1a + t1b)/self.little_m,
            (t2a + t2b)/self.j_term,
            updated_est[0],
            updated_est[1]
        ]

        k2 = np.asarray(k2) * dt

        updated_est = info_vector - k1 + 2 * k2

        t1a = -self.b * updated_est[0] * np.abs(updated_est[0])
        t1b = -self.spring_k1 * (updated_est[2] + self.d2 * updated_est[3])

        t2a = -self.spring_k1 * self.d2 * updated_est[2]
        t2b = -updated_est[3] * (
            self.spring_k1 * (self.d2 ** 2) + self.spring_k2 * (self.d1 ** 2)
        )

        k3 = [
            (t1a + t1b)/self.little_m,
            (t2a + t2b)/self.j_term,
            updated_est[0],
            updated_est[1]
        ]

        k3 = np.asarray(k3) * dt

        final_est = info_vector + (1/6)*(k1 + 4*k2 + k3)

        self.x_dot, self.theta_dot, self.x, self.theta = final_est.copy()
        self.t += dt

    def reset_parms(self, d1=None, d2=None, little_m=None, big_m=None,
                    spring_k1=None, spring_k2=None, b=None,
                    x=None, x_dot=None, theta=None, theta_dot=None,
                    px_len=None, scale=None, pivot=False, method='Euler',
                    dt=None, font_size=None):
        """
        Reset system with a new set of paramters.

        Parameters
        ----------
        d1 : float
            Length of rod (in meters) from pivot to upper spring.
        d2 : float
            Length of rod (in meters) from pivot to lower spring.
        little_m : float
            Mass of attached cube (in kilograms).
        big_m : float
            Mass of rod (in kilograms).
        spring_k1 : float
            Spring constant of lower spring (in N/m).
        spring_k2 : float
            Spring constant of upper spring (in N/m).
        b : float
            Coefficient of quadratic sliding friction (in kg/m).
        x : float
            Initial x-position of mass (in m).
        x_dot : float
            Initial x-velocity of mass (in m/s).
        theta : float
            Initial angle of rod, with respect to vertical (in radians).
        theta_dot : float
            Initial angular velocity of rod (in rad/s).
        px_len : int
            Length of the rod, in pixels.
        scale : int
            Scaling factor to change size of elements.
        pivot : bool
            Switch for showing/hiding pivot point.
        method : str
            Method to use for updating.
        dt : float
            Time step for simulation.
        font_size : float
            Size of font for text elements, in points.

        Notes
        -----

        Since the time is reset, the system is reset as well by calling
        this method.

        """

        self._set_up_system(
            d1=d1, d2=d2, little_m=little_m, big_m=big_m,
            spring_k1=spring_k1, spring_k2=spring_k2, b=b,
            x=x, x_dot=x_dot, theta=theta, theta_dot=theta_dot,
            px_len=px_len, scale=scale, pivot=pivot, method=method,
            dt=dt, font_size=font_size
        )

    def _set_up_system(self, d1=None, d2=None, little_m=None, big_m=None,
                       spring_k1=None, spring_k2=None, b=None,
                       x=None, x_dot=None, theta=None, theta_dot=None,
                       px_len=None, scale=None, pivot=False, method='Euler',
                       dt=None, font_size=None):
        """Initialize constants for the system that will be used later.
        """

        self.method = (string.capwords(method, '-')
                       if method.lower() in VALID_METHODS else 'Euler')
        self.font_size = font_size
        try:
            self.method_text.text = 'Method: {}'.format(self.method)
            self.method_text.font_size = 2 / 3 * self.font_size
            self.text.font_size = self.font_size
        except AttributeError:
            # Running in __init__, so self.method_text isn't established yet.
            pass
        self.show_pivot = pivot

        # Initialize constants for the system
        self.t = 0
        self.dt = 1 / 60 if dt is None else dt
        self.d1 = 0.97 if d1 is None else d1
        self.d2 = 0.55 if d2 is None else d2
        self.little_m = 2.0 if little_m is None else little_m
        self.big_m = 12.5 if big_m is None else big_m
        self.spring_k1 = 1.35 if spring_k1 is None else spring_k1
        self.spring_k2 = 0.5 if spring_k2 is None else spring_k2
        self.b = 25.75 if b is None else b
        self.j_term = (
            (1 / 3) * self.big_m * (self.d1 ** 3 + self.d2 ** 3) /
            (self.d1 + self.d2)
        )
        self.x = -0.010 if x is None else x
        self.x_dot = -0.12 if x_dot is None else x_dot
        self.theta = 0.005 if theta is None else theta
        self.theta_dot = 0.0 if theta_dot is None else theta_dot
        self.theta_not = self.theta  # I'll need this later

        # Initialize constants for display
        self.px_len = 10 if px_len is None else px_len
        self.scale = 50 if scale is None else scale
        self.px_per_m = self.scale * self.px_len / (0.97 + 0.55)
        self.rod_scale = (self.d1 + self.d2) / self.standard_length

        # Set up stuff for establishing a pivot point to rotate about
        self.pivot_loc = (self.d2 - self.d1) / 2
        self.pivot_loc_px = self.pivot_loc * self.px_per_m

        # Set up positioning info for the springs and mass, as well as some
        # constants for use later
        # NOTE: Springs are not like boxes. Their center of rotation is at one
        #       end of the spring, unlike the box where it is in the middle.
        #       The location and scaling is set to reflect this. This means
        #       there's a little bit of x- and y-translation needed to properly
        #       center them.
        self.s2_loc = np.asarray(
            [self.d1 * self.px_per_m * np.sin(self.theta),
             -self.d1 * self.px_per_m * np.cos(
                 self.theta)]
        )
        self.s1_l_not = self.px_len / 4 * self.scale
        self.x_is_0 = (
            -self.d2 * self.px_per_m * np.sin(self.theta_not) -
            1.5 * self.s1_l_not
        )
        self.s1_loc = np.asarray(
            [self.x_is_0 + 0.5 * self.s1_l_not + self.x * self.px_per_m,
             self.d2 * self.px_per_m * np.cos(self.theta)]
        )
        self.mass_loc = np.asarray(
            [self.x_is_0 + self.x * self.px_per_m,
             self.d2 * self.px_per_m * np.cos(self.theta)]
        )


class Paramlist(object):

    def __init__(self, parameters):
        """Container for object parameters.
        Based on methods from ../gloo/primitive_mesh_viewer_qt.
        """
        self.parameters = parameters
        self.props = dict()
        self.props['pivot'] = False
        self.props['method'] = 'Euler'
        for nameV, minV, maxV, typeV, iniV in parameters:
            nameV = CONVERSION_DICT[nameV]
            self.props[nameV] = iniV


class SetupWidget(QtWidgets.QWidget):

    changed_parameter_sig = pyqtsignal(Paramlist)

    def __init__(self, parent=None):
        """Widget for holding all the parameter options in neat lists.
        Based on methods from ../gloo/primitive_mesh_viewer_qt.
        """
        super(SetupWidget, self).__init__(parent)

        # Create the parameter list from the default parameters given here
        self.param = Paramlist(PARAMETERS)

        # Checkbox for whether or not the pivot point is visible
        self.pivot_chk = QtWidgets.QCheckBox(u"Show pivot point")
        self.pivot_chk.setChecked(self.param.props['pivot'])
        self.pivot_chk.toggled.connect(self.update_parameters)

        # A drop-down menu for selecting which method to use for updating
        self.method_list = ['Euler', 'Runge-Kutta']
        self.method_options = QtWidgets.QComboBox()
        self.method_options.addItems(self.method_list)
        self.method_options.setCurrentIndex(
            self.method_list.index((self.param.props['method']))
        )
        self.method_options.currentIndexChanged.connect(
            self.update_parameters
        )

        # Separate the different parameters into groupboxes,
        # so there's a clean visual appearance
        self.parameter_groupbox = QtWidgets.QGroupBox(u"System Parameters")
        self.conditions_groupbox = QtWidgets.QGroupBox(u"Initial Conditions")
        self.display_groupbox = QtWidgets.QGroupBox(u"Display Parameters")

        self.groupbox_list = [self.parameter_groupbox,
                              self.conditions_groupbox,
                              self.display_groupbox]

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        # Get ready to create all the spinboxes with appropriate labels
        plist = []
        self.psets = []
        # important_positions is used to separate the
        # parameters into their appropriate groupboxes
        important_positions = [0, ]
        param_boxes_layout = [QtWidgets.QGridLayout(),
                              QtWidgets.QGridLayout(),
                              QtWidgets.QGridLayout()]
        for nameV, minV, maxV, typeV, iniV in self.param.parameters:
            # Create Labels for each element
            plist.append(QtWidgets.QLabel(nameV))

            if nameV == 'x' or nameV == 'scale':
                # 'x' is the start of the 'Initial Conditions' groupbox,
                # 'scale' is the start of the 'Display Parameters' groupbox
                important_positions.append(len(plist) - 1)

            # Create Spinboxes based on type - doubles get a DoubleSpinBox,
            # ints get regular SpinBox.
            # Step sizes are the same for every parameter except font size.
            if typeV == 'double':
                self.psets.append(QtWidgets.QDoubleSpinBox())
                self.psets[-1].setDecimals(3)
                if nameV == 'font size':
                    self.psets[-1].setSingleStep(1.0)
                else:
                    self.psets[-1].setSingleStep(0.01)
            elif typeV == 'int':
                self.psets.append(QtWidgets.QSpinBox())

            # Set min, max, and initial values
            self.psets[-1].setMaximum(maxV)
            self.psets[-1].setMinimum(minV)
            self.psets[-1].setValue(iniV)

        pidx = -1
        for pos in range(len(plist)):
            if pos in important_positions:
                pidx += 1
            param_boxes_layout[pidx].addWidget(plist[pos], pos + pidx, 0)
            param_boxes_layout[pidx].addWidget(self.psets[pos], pos + pidx, 1)
            self.psets[pos].valueChanged.connect(self.update_parameters)

        param_boxes_layout[0].addWidget(QtWidgets.QLabel('Method: '), 8, 0)
        param_boxes_layout[0].addWidget(self.method_options, 8, 1)
        param_boxes_layout[-1].addWidget(self.pivot_chk, 2, 0, 3, 0)

        for groupbox, layout in zip(self.groupbox_list, param_boxes_layout):
            groupbox.setLayout(layout)

        for groupbox in self.groupbox_list:
            self.splitter.addWidget(groupbox)

        vbox = QtWidgets.QVBoxLayout()
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.splitter)
        hbox.addStretch(5)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def update_parameters(self, option):
        """When the system parameters change, get the state and emit it."""
        self.param.props['pivot'] = self.pivot_chk.isChecked()
        self.param.props['method'] = self.method_list[
            self.method_options.currentIndex()
        ]
        keys = map(lambda x: x[0], self.param.parameters)
        for pos, nameV in enumerate(keys):
            self.param.props[CONVERSION_DICT[nameV]] = self.psets[pos].value()
        self.changed_parameter_sig.emit(self.param)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, param=None):
        """Main Window for holding the Vispy Canvas and the parameter
        control menu.
        """
        QtWidgets.QMainWindow.__init__(self)

        self.resize(1067, 800)
        icon = load_data_file('wiggly_bar/spring.ico')
        self.setWindowIcon(QtGui.QIcon(icon))
        self.setWindowTitle('Nonlinear Physical Model Simulation')

        self.parameter_object = SetupWidget(self)
        self.parameter_object.param = (param
                                       if param is not None else
                                       self.parameter_object.param)
        self.parameter_object.changed_parameter_sig.connect(self.update_view)

        self.view_box = WigglyBar(**self.parameter_object.param.props)

        self.view_box.create_native()
        self.view_box.native.setParent(self)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.parameter_object)
        splitter.addWidget(self.view_box.native)

        self.setCentralWidget(splitter)

    def update_view(self, param):
        """Update the VisPy canvas when the parameters change.
        """
        self.view_box.reset_parms(**param.props)


def uncaught_exceptions(ex_type, ex_value, ex_traceback):
    lines = traceback.format_exception(ex_type, ex_value, ex_traceback)
    msg = ''.join(lines)
    logger.error('Uncaught Exception\n%s', msg)


def main():
    sys.excepthook = uncaught_exceptions
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().setLevel(logging.INFO)
    appQt = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    appQt.exec_()

if __name__ == '__main__':
    main()
