# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Tests for RegularPolygonVisual
All images are of size (100,100) to keep a small file size
"""

from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@requires_application()
def test_regular_polygon_draw1():
    """Test drawing regular polygons without transforms using RegularPolygonVisual"""  # noqa
    with TestingCanvas() as c:
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(1, 0, 0, 1))
        rpolygon.transform = transforms.STTransform(scale=(50, 50),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_approved("screenshot", 'visuals/regular_polygon1.png')

        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(1, 0, 0, 1),
                                          border_color=(0, 1, 1, 1))
        rpolygon.transform = transforms.STTransform(scale=(50, 50),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_approved("screenshot", 'visuals/regular_polygon2.png')

        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          border_color=(0, 1, 1, 1))
        rpolygon.transform = transforms.STTransform(scale=(50, 50),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_approved("screenshot", 'visuals/regular_polygon3.png',
                              min_corr=0.7)


@requires_application()
def test_regular_polygon_draw2():
    """Test drawing transformed regular polygons using RegularPolygonVisual"""  # noqa
    with TestingCanvas() as c:
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(0, 0, 1, 1))
        rpolygon.transform = transforms.STTransform(scale=(75, 100),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_approved("screenshot", 'visuals/regular_polygon4.png')

        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(0, 0, 1, 1),
                                          border_color=(1, 0, 0, 1))
        rpolygon.transform = transforms.STTransform(scale=(75, 100),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_approved("screenshot", 'visuals/regular_polygon5.png')

        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          border_color=(1, 0, 0, 1))
        rpolygon.transform = transforms.STTransform(scale=(75, 100),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_approved("screenshot", 'visuals/regular_polygon6.png', 
                              min_corr=0.6)


@requires_application()
def test_reactive_draw():
    """Test reactive regular polygon attributes"""
    with TestingCanvas() as c:
        rpolygon = visuals.RegularPolygon(pos=[50, 50, 0.], radius=20, sides=8,
                                          color='yellow')
        c.draw_visual(rpolygon)

        rpolygon.pos = [70, 40, 0.]
        c.draw_visual(rpolygon)
        assert_image_approved("screenshot",
                              'visuals/reactive_regular_polygon1.png')

        rpolygon.radius = 25
        c.draw_visual(rpolygon)
        assert_image_approved("screenshot",
                              'visuals/reactive_regular_polygon2.png')

        rpolygon.color = 'red'
        c.draw_visual(rpolygon)
        assert_image_approved("screenshot",
                              'visuals/reactive_regular_polygon3.png')

        rpolygon.border_color = 'yellow'
        c.draw_visual(rpolygon)
        assert_image_approved("screenshot",
                              'visuals/reactive_regular_polygon4.png')

        rpolygon.sides = 6
        c.draw_visual(rpolygon)
        assert_image_approved("screenshot",
                              'visuals/reactive_regular_polygon5.png')


run_tests_if_main()
