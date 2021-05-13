from __future__ import division

import numpy as np
from math import gcd


class TorusKnot(object):
    """Representation of a torus knot or link.

    A torus knot is one that can be drawn on the surface of a
    torus. It is parameterised by two integers p and q as below; in
    fact this returns a single knot (a single curve) only if p and q
    are coprime, otherwise it describes multiple linked curves.

    Parameters
    ----------
    p : int
        The number of times the knot winds around the outside of the
        torus. Defaults to 2.
    q : int
        The number of times the knot passes through the hole in the
        centre of the torus. Defaults to 3.
    num_points : int
        The number of points in the returned piecewise linear
        curve. If there are multiple curves (i.e. a torus link), this
        is the number of points in *each* curve.  Defaults to 100.
    major_radius : float
        Distance from the center of the torus tube to the center of the torus.
        Defaults to 10.
    minor_radius : float
        The radius of the torus tube. Defaults to 5.

    """

    def __init__(self, p=3, q=2, num_points=100, major_radius=10.,
                 minor_radius=5.):
        self._p = p
        self._q = q
        self._num_points = num_points
        self._major_radius = major_radius
        self._minor_radius = minor_radius

        self._calculate_vertices()

    def _calculate_vertices(self):
        angles = np.linspace(0, 2*np.pi, self._num_points)

        num_components = self.num_components

        divisions = (np.max([self._q, self._p]) *
                     np.min([self._q, self._p]) // self.num_components)
        starting_angles = np.linspace(
            0, 2*np.pi, divisions + 1)[
            :num_components]
        q = self._q / num_components
        p = self._p / num_components

        components = []
        for starting_angle in starting_angles:
            vertices = np.zeros((self._num_points, 3))
            local_angles = angles + starting_angle
            radii = (self._minor_radius * np.cos(q * angles) +
                     self._major_radius)
            vertices[:, 0] = radii * np.cos(p * local_angles)
            vertices[:, 1] = radii * np.sin(p * local_angles)
            vertices[:, 2] = (self._minor_radius * -1 *
                              np.sin(q * angles))
            components.append(vertices)

        self._components = components

    @property
    def first_component(self):
        """The vertices of the first component line of the torus knot or link."""
        return self._components[0]

    @property
    def components(self):
        """A list of the vertices in each line of the torus knot or link.
        Even if p and q are coprime, this is a list with just one
        entry.
        """
        return self._components

    @property
    def num_components(self):
        """The number of component lines in the torus link. This is equal
        to the greatest common divisor of p and q.
        """
        return gcd(self._p, self._q)

    @property
    def q(self):
        """The q parameter of the torus knot or link."""
        return self._q

    @q.setter
    def q(self, q):
        self._q = q
        self._calculate_vertices()

    @property
    def p(self):
        """The p parameter of the torus knot or link."""
        return self._p

    @p.setter
    def p(self, p):
        self._p = p
        self._calculate_vertices()

    @property
    def minor_radius(self):
        """The minor radius of the torus."""
        return self._minor_radius

    @minor_radius.setter
    def minor_radius(self, r):
        self._minor_radius = r
        self._calculate_vertices()

    @property
    def major_radius(self):
        """The major radius of the torus."""
        return self._major_radius

    @major_radius.setter
    def major_radius(self, r):
        self._major_radius = r
        self._calculate_vertices()

    @property
    def num_points(self):
        """The number of points in the vertices returned for each knot/link
        component
        """
        return self._num_points

    @num_points.setter
    def num_points(self, r):
        self._num_points = r
        self._calculate_vertices()
