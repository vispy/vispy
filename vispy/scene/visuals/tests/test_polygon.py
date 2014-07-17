# -*- coding: utf-8 -*-

"""
Tests for PolygonVisual
All images are of size (100,100) to keep a small file size
"""


import numpy as np
from numpy.testing import assert_array_equal
from vispy.app import Canvas
from vispy import gloo
from vispy.gloo.util import _screenshot
from vispy.scene import visuals, transforms
from vispy.testing import requires_application
from vispy.util.dataio import imread, _check_img_lib
from vispy.util import get_test_file

has_img_lib = not all(c is None for c in _check_img_lib())
requires_img_lib = np.testing.dec.skipif(not has_img_lib, 'imageio or PIL '
                                         'required')


@requires_application()
@requires_img_lib
def test_square_draw1():
    """Test drawing a simple borderless square using PolygonVisual"""
    pos = np.array([[-0.5, 0.5, 0],
                    [0.5, 0.5, 0],
                    [0.5, -0.5, 0],
                    [-0.5, -0.5, 0]])
    with Canvas(size=(100, 100)) as c:
        c.polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.polygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/square1.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_square_draw2():
    """Test drawing a simple square with border using PolygonVisual"""
    pos = np.array([[-0.5, 0.5, 0],
                    [0.5, 0.5, 0],
                    [0.5, -0.5, 0],
                    [-0.5, -0.5, 0]])
    with Canvas(size=(100, 100)) as c:
        c.polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1),
                                    border_color=(1, 1, 1, 1))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.polygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/square2.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_square_draw3():
    """Test drawing an empty square border using PolygonVisual"""
    pos = np.array([[-0.5, 0.5, 0],
                    [0.5, 0.5, 0],
                    [0.5, -0.5, 0],
                    [-0.5, -0.5, 0]])
    with Canvas(size=(100, 100)) as c:
        c.polygon = visuals.Polygon(pos=pos, border_color=(1, 1, 1, 1))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.polygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/square3.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_rectangle_draw1():
    """Test drawing a transformed borderless rectangle using PolygonVisual"""
    pos = np.array([[-0.1, 0.5, 0],
                    [0.1, 0.5, 0],
                    [0.1, -0.5, 0],
                    [-0.1, -0.5, 0]])
    with Canvas(size=(100, 100)) as c:
        c.polygon = visuals.Polygon(pos=pos, color=(1, 1, 0, 1))
        c.polygon.transform = transforms.STTransform(scale=(4.0, 0.5))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.polygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/rectangle1.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_rectangle_draw2():
    """Test drawing a transformed rectangle with border using PolygonVisual"""
    pos = np.array([[-0.1, 0.5, 0],
                    [0.1, 0.5, 0],
                    [0.1, -0.5, 0],
                    [-0.1, -0.5, 0]])
    with Canvas(size=(100, 100)) as c:
        c.polygon = visuals.Polygon(pos=pos, color=(1, 1, 0, 1),
                                    border_color=(1, 0, 0, 1))
        c.polygon.transform = transforms.STTransform(scale=(4.0, 0.5))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.polygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/rectangle2.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_rectangle_draw3():
    """Test drawing a transformed empty rectangle border using PolygonVisual"""
    pos = np.array([[-0.1, 0.5, 0],
                    [0.1, 0.5, 0],
                    [0.1, -0.5, 0],
                    [-0.1, -0.5, 0]])
    with Canvas(size=(100, 100)) as c:
        c.polygon = visuals.Polygon(pos=pos, border_color=(1, 0, 0, 1))
        c.polygon.transform = transforms.STTransform(scale=(4.0, 0.5))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.polygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/rectangle3.png'))
        assert_array_equal(im, ss)
