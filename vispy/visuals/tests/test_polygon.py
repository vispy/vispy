# -*- coding: utf-8 -*-

"""
Tests for PolygonVisual
All images are of size (100,100) to keep a small file size
"""

import numpy as np

from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, requires_scipy, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@requires_application()
@requires_scipy()
def test_square_draw():
    """Test drawing squares without transforms using PolygonVisual"""
    pos = np.array([[-0.5, 0.5, 0],
                    [0.5, 0.5, 0],
                    [0.5, -0.5, 0],
                    [-0.5, -0.5, 0]])
    with TestingCanvas() as c:
        polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1),
                                  parent=c.scene)
        polygon.transform = transforms.STTransform(scale=(50, 50),
                                                   translate=(50, 50))

        assert_image_approved(c.render(), 'visuals/square1.png')

        polygon.parent = None
        polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1),
                                  border_color=(1, 1, 1, 1),
                                  parent=c.scene)
        polygon.transform = transforms.STTransform(scale=(50, 50),
                                                   translate=(50, 50))

        assert_image_approved(c.render(), 'visuals/square2.png')

        polygon.parent = None
        polygon = visuals.Polygon(pos=pos, border_color=(1, 1, 1, 1),
                                  parent=c.scene)
        polygon.transform = transforms.STTransform(scale=(50, 50),
                                                   translate=(50, 50))

        assert_image_approved(c.render(), 'visuals/square3.png',
                              min_corr=0.45)


@requires_application()
@requires_scipy()
def test_rectangle_draw():
    """Test drawing rectangles with transforms using PolygonVisual"""
    pos = np.array([[-0.1, 0.5, 0],
                    [0.1, 0.5, 0],
                    [0.1, -0.5, 0],
                    [-0.1, -0.5, 0]])
    with TestingCanvas() as c:
        polygon = visuals.Polygon(pos=pos, color=(1, 1, 0, 1), parent=c.scene)
        polygon.transform = transforms.STTransform(scale=(200.0, 25),
                                                   translate=(50, 50))

        assert_image_approved(c.render(), 'visuals/rectangle1.png')

        polygon.parent = None
        polygon = visuals.Polygon(pos=pos, color=(1, 1, 0, 1),
                                  border_color=(1, 0, 0, 1),
                                  parent=c.scene)
        polygon.transform = transforms.STTransform(scale=(200.0, 25),
                                                   translate=(50, 50))

        assert_image_approved(c.render(), 'visuals/rectangle2.png')

        polygon.parent = None
        polygon = visuals.Polygon(pos=pos, border_color=(1, 0, 0, 1),
                                  border_width=1, parent=c.scene)
        polygon.transform = transforms.STTransform(scale=(200.0, 25),
                                                   translate=(50, 49))

        assert_image_approved(c.render(), 'visuals/rectangle3.png',
                              min_corr=0.7)


@requires_application()
@requires_scipy()
def test_reactive_draw():
    """Test reactive polygon attributes"""
    pos = np.array([[-0.1, 0.5, 0],
                    [0.1, 0.5, 0],
                    [0.1, -0.5, 0],
                    [-0.1, -0.5, 0]])
    with TestingCanvas() as c:
        polygon = visuals.Polygon(pos=pos, color='yellow', parent=c.scene)
        polygon.transform = transforms.STTransform(scale=(50, 50),
                                                   translate=(50, 50))

        polygon.pos += [0.1, -0.1, 0]

        assert_image_approved(c.render(), 'visuals/reactive_polygon1.png')

        polygon.color = 'red'

        assert_image_approved(c.render(), 'visuals/reactive_polygon2.png')

        polygon.border_color = 'yellow'

        assert_image_approved(c.render(), 'visuals/reactive_polygon3.png',
                              min_corr=0.8)


run_tests_if_main()
