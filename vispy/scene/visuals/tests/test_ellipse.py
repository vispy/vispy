# -*- coding: utf-8 -*-

"""
Tests for EllipseVisual
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
def test_circle_draw1():
    """Test drawing a simple borderless circle using EllipseVisual"""
    with Canvas(size=(100, 100)) as c:
        c.ellipse = visuals.Ellipse(pos=(0.5, 0.3, 0), radius=0.4,
                                    color=(1, 0, 0, 1))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.ellipse.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/circle1.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_circle_draw2():
    """Test drawing a simple circle with border using EllipseVisual"""
    with Canvas(size=(100, 100)) as c:
        c.ellipse = visuals.Ellipse(pos=(0.5, 0.3, 0), radius=0.4,
                                    color=(1, 0, 0, 1),
                                    border_color=(0, 1, 1, 1))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.ellipse.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/circle2.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_circle_draw3():
    """Test drawing an empty circle border using EllipseVisual"""
    with Canvas(size=(100, 100)) as c:
        c.ellipse = visuals.Ellipse(pos=(0.5, 0.3, 0), radius=0.4,
                                    border_color=(0, 1, 1, 1))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.ellipse.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/circle3.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_ellipse_draw1():
    """Test drawing a transformed borderless ellipse using EllipseVisual"""
    with Canvas(size=(100, 100)) as c:
        c.ellipse = visuals.Ellipse(pos=(0., 0.), radius=(0.4, 0.3),
                                    color=(0, 0, 1, 1))
        c.ellipse.transform = transforms.STTransform(scale=(2.0, 3.0))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.ellipse.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/ellipse1.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_ellipse_draw2():
    """Test drawing a transformed ellipse with border using EllipseVisual"""
    with Canvas(size=(100, 100)) as c:
        c.ellipse = visuals.Ellipse(pos=(0., 0.), radius=(0.4, 0.3),
                                    color=(0, 0, 1, 1),
                                    border_color=(1, 0, 0, 1))
        c.ellipse.transform = transforms.STTransform(scale=(2.0, 3.0))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.ellipse.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/ellipse2.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_ellipse_draw3():
    """Test drawing a transformed empty ellipse border using EllipseVisual"""
    with Canvas(size=(100, 100)) as c:
        c.ellipse = visuals.Ellipse(pos=(0., 0.), radius=(0.4, 0.3),
                                    border_color=(1, 0, 0, 1))
        c.ellipse.transform = transforms.STTransform(scale=(2.0, 3.0))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.ellipse.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/ellipse3.png'))
        assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_arc_draw1():
    """Test drawing a filled arc using EllipseVisual"""
    with Canvas(size=(100, 100)) as c:
        c.ellipse = visuals.Ellipse(pos=(0., 0.), radius=(0.4, 0.3),
                                    start_angle=90., span_angle=120.,
                                    color=(0, 0, 1, 1))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.ellipse.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/arc1.png'))
            assert_array_equal(im, ss)


@requires_application()
@requires_img_lib
def test_arc_draw2():
    """Test drawing an arc using EllipseVisual"""
    with Canvas(size=(100, 100)) as c:
        c.ellipse = visuals.Ellipse(pos=(0., 0.), radius=(0.4, 0.3),
                                    start_angle=90., span_angle=120.,
                                    border_color=(1, 0, 0, 1))
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *c.size)
        c.ellipse.draw()
        ss = _screenshot(alpha=False)
        im = imread(get_test_file('visuals/arc2.png'))
        assert_array_equal(im, ss)
