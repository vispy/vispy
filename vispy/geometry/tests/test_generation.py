# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np
from numpy.testing import assert_array_equal, assert_allclose

from vispy.testing import run_tests_if_main
from vispy.geometry import (create_box, create_cube, create_cylinder,
                            create_sphere, create_plane)


def test_box():
    """Test box function"""
    vertices, filled, outline = create_box()
    assert_array_equal(np.arange(len(vertices)), np.unique(filled))
    assert_array_equal(np.arange(len(vertices)), np.unique(outline))


def test_cube():
    """Test cube function"""
    vertices, filled, outline = create_cube()
    assert_array_equal(np.arange(len(vertices)), np.unique(filled))
    assert_array_equal(np.arange(len(vertices)), np.unique(outline))


def test_sphere():
    """Test sphere function"""
    md = create_sphere(rows=10, cols=20, radius=10, method='latitude')
    radii = np.sqrt((md.get_vertices() ** 2).sum(axis=1))
    assert_allclose(radii, np.ones_like(radii) * 10)
    md = create_sphere(subdivisions=5, radius=10, method='ico')
    radii = np.sqrt((md.get_vertices() ** 2).sum(axis=1))
    assert_allclose(radii, np.ones_like(radii) * 10)
    md = create_sphere(rows=20, cols=20, depth=20, radius=10, method='cube')
    radii = np.sqrt((md.get_vertices() ** 2).sum(axis=1))
    assert_allclose(radii, np.ones_like(radii) * 10)


def test_cylinder():
    """Test cylinder function"""
    md = create_cylinder(10, 20, radius=[10, 10])
    radii = np.sqrt((md.get_vertices()[:, :2] ** 2).sum(axis=1))
    assert_allclose(radii, np.ones_like(radii) * 10)


def test_plane():
    """Test plane function"""
    vertices, filled, outline = create_plane()
    assert_array_equal(np.arange(len(vertices)), np.unique(filled))
    assert_array_equal(np.arange(len(vertices)), np.unique(outline))


run_tests_if_main()
