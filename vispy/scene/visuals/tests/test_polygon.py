# -*- coding: utf-8 -*-

"""
Tests for PolygonVisual
All images are of size (100,100) to keep a small file size
"""

import numpy as np
from vispy.app import TestingCanvas
from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, assert_image_equal,
                           requires_img_lib)


@requires_application()
@requires_img_lib()
def test_square_draw1():
    """Test drawing a simple borderless square using PolygonVisual"""
    pos = np.array([[-0.5, 0.5, 0],
                    [0.5, 0.5, 0],
                    [0.5, -0.5, 0],
                    [-0.5, -0.5, 0]])
    with TestingCanvas():
        polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1))
        polygon.draw()
        assert_image_equal("screenshot", 'visuals/square1.png')


@requires_application()
@requires_img_lib()
def test_square_draw2():
    """Test drawing a simple square with border using PolygonVisual"""
    pos = np.array([[-0.5, 0.5, 0],
                    [0.5, 0.5, 0],
                    [0.5, -0.5, 0],
                    [-0.5, -0.5, 0]])
    with TestingCanvas():
        polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1),
                                  border_color=(1, 1, 1, 1))
        polygon.draw()
        assert_image_equal("screenshot", 'visuals/square2.png')


@requires_application()
@requires_img_lib()
def test_square_draw3():
    """Test drawing an empty square border using PolygonVisual"""
    pos = np.array([[-0.5, 0.5, 0],
                    [0.5, 0.5, 0],
                    [0.5, -0.5, 0],
                    [-0.5, -0.5, 0]])
    with TestingCanvas():
        polygon = visuals.Polygon(pos=pos, border_color=(1, 1, 1, 1))
        polygon.draw()
        assert_image_equal("screenshot", 'visuals/square3.png')


@requires_application()
@requires_img_lib()
def test_rectangle_draw1():
    """Test drawing a transformed borderless rectangle using PolygonVisual"""
    pos = np.array([[-0.1, 0.5, 0],
                    [0.1, 0.5, 0],
                    [0.1, -0.5, 0],
                    [-0.1, -0.5, 0]])
    with TestingCanvas():
        polygon = visuals.Polygon(pos=pos, color=(1, 1, 0, 1))
        polygon.transform = transforms.STTransform(scale=(4.0, 0.5))
        polygon.draw()
        assert_image_equal("screenshot", 'visuals/rectangle1.png')


@requires_application()
@requires_img_lib()
def test_rectangle_draw2():
    """Test drawing a transformed rectangle with border using PolygonVisual"""
    pos = np.array([[-0.1, 0.5, 0],
                    [0.1, 0.5, 0],
                    [0.1, -0.5, 0],
                    [-0.1, -0.5, 0]])
    with TestingCanvas():
        polygon = visuals.Polygon(pos=pos, color=(1, 1, 0, 1),
                                  border_color=(1, 0, 0, 1))
        polygon.transform = transforms.STTransform(scale=(4.0, 0.5))
        polygon.draw()
        assert_image_equal("screenshot", 'visuals/rectangle2.png')


@requires_application()
@requires_img_lib()
def test_rectangle_draw3():
    """Test drawing a transformed empty rectangle border using PolygonVisual"""
    pos = np.array([[-0.1, 0.5, 0],
                    [0.1, 0.5, 0],
                    [0.1, -0.5, 0],
                    [-0.1, -0.5, 0]])
    with TestingCanvas():
        polygon = visuals.Polygon(pos=pos, border_color=(1, 0, 0, 1))
        polygon.transform = transforms.STTransform(scale=(4.0, 0.5))
        polygon.draw()
        assert_image_equal("screenshot", 'visuals/rectangle3.png')
