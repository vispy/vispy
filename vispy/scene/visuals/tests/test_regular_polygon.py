# -*- coding: utf-8 -*-

"""
Tests for RegularPolygonVisual
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
def test_regular_polygon_draw1():
    """Test drawing a simple borderless regular polygon using
    RegularPolygonVisual"""
    with Canvas(size=(100, 100)) as c:
        c.rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                            color=(1, 0, 0, 1))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.rpolygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/regular_polygon1.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_regular_polygon_draw2():
    """Test drawing a simple regular polygon with border using
    RegularPolygonVisual"""
    with Canvas(size=(100, 100)) as c:
        c.rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                            color=(1, 0, 0, 1),
                                            border_color=(0, 1, 1, 1))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.rpolygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/regular_polygon2.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_regular_polygon_draw3():
    """Test drawing an empty regular polygon border using
    RegularPolygonVisual"""
    with Canvas(size=(100, 100)) as c:
        c.rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                            border_color=(0, 1, 1, 1))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.rpolygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/regular_polygon3.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_regular_polygon_draw4():
    """Test drawing a transformed borderless regular polygon using
    RegularPolygonVisual"""
    with Canvas(size=(100, 100)) as c:
        c.rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                            color=(0, 0, 1, 1))
        c.rpolygon.transform = transforms.STTransform(scale=(1.5, 2.0))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.rpolygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/regular_polygon4.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_regular_polygon_draw5():
    """Test drawing a transformed regular polygon with border using
    RegularPolygonVisual"""
    with Canvas(size=(100, 100)) as c:
        c.rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                            color=(0, 0, 1, 1),
                                            border_color=(1, 0, 0, 1))
        c.rpolygon.transform = transforms.STTransform(scale=(1.5, 2.0))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.rpolygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/regular_polygon5.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_regular_polygon_draw6():
    """Test drawing a transformed empty regular polygon border using
    RegularPolygonVisual"""
    with Canvas(size=(100, 100)) as c:
        c.rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                            border_color=(1, 0, 0, 1))
        c.rpolygon.transform = transforms.STTransform(scale=(1.5, 2.0))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.rpolygon.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/regular_polygon6.png'))
        assert_array_equal(im, ss)
