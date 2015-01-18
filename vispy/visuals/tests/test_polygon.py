# -*- coding: utf-8 -*-

"""
Tests for PolygonVisual
All images are of size (100,100) to keep a small file size
"""

import numpy as np

from vispy import gloo
from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, assert_image_equal,
                           requires_scipy, TestingCanvas,
                           run_tests_if_main)


@requires_application()
@requires_scipy()
def test_square_draw():
    """Test drawing squares without transforms using PolygonVisual"""
    pos = np.array([[-0.5, 0.5, 0],
                    [0.5, 0.5, 0],
                    [0.5, -0.5, 0],
                    [-0.5, -0.5, 0]])
    with TestingCanvas() as c:
        polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1))
        polygon.transform = transforms.STTransform(scale=(50, 50),
                                                   translate=(50, 50))
        c.draw_visual(polygon)
        assert_image_equal("screenshot", 'visuals/square1.png')

        gloo.clear()
        polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1),
                                  border_color=(1, 1, 1, 1))
        polygon.transform = transforms.STTransform(scale=(50, 50),
                                                   translate=(50, 50))
        c.draw_visual(polygon)
        assert_image_equal("screenshot", 'visuals/square2.png')

        gloo.clear()
        polygon = visuals.Polygon(pos=pos, border_color=(1, 1, 1, 1))
        polygon.transform = transforms.STTransform(scale=(50, 50),
                                                   translate=(50, 50))
        c.draw_visual(polygon)
        assert_image_equal("screenshot", 'visuals/square3.png')


@requires_application()
@requires_scipy()
def test_rectangle_draw():
    """Test drawing rectangles with transforms using PolygonVisual"""
    pos = np.array([[-0.1, 0.5, 0],
                    [0.1, 0.5, 0],
                    [0.1, -0.5, 0],
                    [-0.1, -0.5, 0]])
    with TestingCanvas() as c:
        polygon = visuals.Polygon(pos=pos, color=(1, 1, 0, 1))
        polygon.transform = transforms.STTransform(scale=(200.0, 25),
                                                   translate=(50, 50))
        c.draw_visual(polygon)
        assert_image_equal("screenshot", 'visuals/rectangle1.png')

        gloo.clear()
        polygon = visuals.Polygon(pos=pos, color=(1, 1, 0, 1),
                                  border_color=(1, 0, 0, 1))
        polygon.transform = transforms.STTransform(scale=(200.0, 25),
                                                   translate=(50, 50))
        c.draw_visual(polygon)
        assert_image_equal("screenshot", 'visuals/rectangle2.png')

        gloo.clear()
        polygon = visuals.Polygon(pos=pos, border_color=(1, 0, 0, 1),
                                  border_width=1)
        polygon.transform = transforms.STTransform(scale=(200.0, 25),
                                                   translate=(50, 49))
        c.draw_visual(polygon)
        assert_image_equal("screenshot", 'visuals/rectangle3.png')


@requires_application()
@requires_scipy()
def test_reactive_draw():
    """Test reactive polygon attributes"""
    pos = np.array([[-0.1, 0.5, 0],
                    [0.1, 0.5, 0],
                    [0.1, -0.5, 0],
                    [-0.1, -0.5, 0]])
    with TestingCanvas() as c:
        polygon = visuals.Polygon(pos=pos, color='yellow')
        polygon.transform = transforms.STTransform(scale=(50, 50),
                                                   translate=(50, 50))
        c.draw_visual(polygon)

        gloo.clear()
        polygon.pos += [0.1, -0.1, 0]
        c.draw_visual(polygon)
        assert_image_equal("screenshot", 'visuals/reactive_polygon1.png')

        gloo.clear()
        polygon.color = 'red'
        c.draw_visual(polygon)
        assert_image_equal("screenshot", 'visuals/reactive_polygon2.png')

        gloo.clear()
        polygon.border_color = 'yellow'
        c.draw_visual(polygon)
        assert_image_equal("screenshot", 'visuals/reactive_polygon3.png')


run_tests_if_main()
