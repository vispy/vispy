# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np
from numpy.testing import assert_array_equal, assert_allclose

from vispy.geometry import create_cube, create_cylinder, create_sphere


def test_cube():
    """Test cube function"""
    vertices, filled, outline = create_cube()
    assert_array_equal(np.arange(len(vertices)), np.unique(filled))
    assert_array_equal(np.arange(len(vertices)), np.unique(outline))


def test_sphere():
    """Test sphere function"""
    md = create_sphere(10, 20, radius=10)
    radii = np.sqrt((md.vertices() ** 2).sum(axis=1))
    assert_allclose(radii, np.ones_like(radii) * 10)


def test_cylinder():
    """Test cylinder function"""
    md = create_cylinder(10, 20, radius=[10, 10])
    radii = np.sqrt((md.vertices()[:, :2] ** 2).sum(axis=1))
    assert_allclose(radii, np.ones_like(radii) * 10)
