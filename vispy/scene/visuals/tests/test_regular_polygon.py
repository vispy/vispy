# -*- coding: utf-8 -*-

"""
Tests for RegularPolygonVisual
All images are of size (100,100) to keep a small file size
"""

from vispy.app import TestingCanvas
from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, assert_image_equal,
                           requires_img_lib)


@requires_application()
@requires_img_lib()
def test_regular_polygon_draw1():
    """Test drawing a simple borderless regular polygon using
    RegularPolygonVisual"""
    with TestingCanvas():
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(1, 0, 0, 1))
        rpolygon.draw()
        assert_image_equal("screenshot", 'visuals/regular_polygon1.png')


@requires_application()
@requires_img_lib()
def test_regular_polygon_draw2():
    """Test drawing a simple regular polygon with border using
    RegularPolygonVisual"""
    with TestingCanvas():
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(1, 0, 0, 1),
                                          border_color=(0, 1, 1, 1))
        rpolygon.draw()
        assert_image_equal("screenshot", 'visuals/regular_polygon2.png')


@requires_application()
@requires_img_lib()
def test_regular_polygon_draw3():
    """Test drawing an empty regular polygon border using
    RegularPolygonVisual"""
    with TestingCanvas():
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          border_color=(0, 1, 1, 1))
        rpolygon.draw()
        assert_image_equal("screenshot", 'visuals/regular_polygon3.png')


@requires_application()
@requires_img_lib()
def test_regular_polygon_draw4():
    """Test drawing a transformed borderless regular polygon using
    RegularPolygonVisual"""
    with TestingCanvas():
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(0, 0, 1, 1))
        rpolygon.transform = transforms.STTransform(scale=(1.5, 2.0))
        rpolygon.draw()
        assert_image_equal("screenshot", 'visuals/regular_polygon4.png')


@requires_application()
@requires_img_lib()
def test_regular_polygon_draw5():
    """Test drawing a transformed regular polygon with border using
    RegularPolygonVisual"""
    with TestingCanvas():
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(0, 0, 1, 1),
                                          border_color=(1, 0, 0, 1))
        rpolygon.transform = transforms.STTransform(scale=(1.5, 2.0))
        rpolygon.draw()
        assert_image_equal("screenshot", 'visuals/regular_polygon5.png')


@requires_application()
@requires_img_lib()
def test_regular_polygon_draw6():
    """Test drawing a transformed empty regular polygon border using
    RegularPolygonVisual"""
    with TestingCanvas():
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          border_color=(1, 0, 0, 1))
        rpolygon.transform = transforms.STTransform(scale=(1.5, 2.0))
        rpolygon.draw()
        assert_image_equal("screenshot", 'visuals/regular_polygon6.png')
