# -*- coding: utf-8 -*-

"""
Tests for RegularPolygonVisual
All images are of size (100,100) to keep a small file size
"""

import sys

from vispy import gloo
from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, assert_image_equal,
                           TestingCanvas, SkipTest)


@requires_application()
def test_regular_polygon_draw1():
    """Test drawing regular polygons without transforms using RegularPolygonVisual"""  # noqa
    
    # TODO: remove this skip after fixing 
    # https://github.com/vispy/vispy/issues/374
    if sys.version[0] == '3':
        raise SkipTest
    
    with TestingCanvas() as c:
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(1, 0, 0, 1))
        rpolygon.transform = transforms.STTransform(scale=(50, 50),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_equal("screenshot", 'visuals/regular_polygon1.png')

        gloo.clear()
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(1, 0, 0, 1),
                                          border_color=(0, 1, 1, 1))
        rpolygon.transform = transforms.STTransform(scale=(50, 50),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_equal("screenshot", 'visuals/regular_polygon2.png')

        gloo.clear()
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          border_color=(0, 1, 1, 1))
        rpolygon.transform = transforms.STTransform(scale=(50, 50),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_equal("screenshot", 'visuals/regular_polygon3.png')


@requires_application()
def test_regular_polygon_draw2():
    """Test drawing transformed regular polygons using RegularPolygonVisual"""  # noqa
    
    # TODO: remove this skip after fixing 
    # https://github.com/vispy/vispy/issues/374
    if sys.version[0] == '3':
        raise SkipTest
    
    with TestingCanvas() as c:
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(0, 0, 1, 1))
        rpolygon.transform = transforms.STTransform(scale=(75, 100),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_equal("screenshot", 'visuals/regular_polygon4.png')

        gloo.clear()
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          color=(0, 0, 1, 1),
                                          border_color=(1, 0, 0, 1))
        rpolygon.transform = transforms.STTransform(scale=(75, 100),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_equal("screenshot", 'visuals/regular_polygon5.png')

        gloo.clear()
        rpolygon = visuals.RegularPolygon(pos=(0., 0.), radius=0.4, sides=8,
                                          border_color=(1, 0, 0, 1))
        rpolygon.transform = transforms.STTransform(scale=(75, 100),
                                                    translate=(50, 50))
        c.draw_visual(rpolygon)
        assert_image_equal("screenshot", 'visuals/regular_polygon6.png')


@requires_application()
def test_reactive_draw():
    """Test reactive regular polygon attributes"""
    
    # TODO: remove this skip after fixing 
    # https://github.com/vispy/vispy/issues/374
    if sys.version[0] == '3':
        raise SkipTest

    with TestingCanvas() as c:
        rpolygon = visuals.RegularPolygon(pos=[50, 50, 0.], radius=20, sides=8,
                                          color='yellow')
        c.draw_visual(rpolygon)

        gloo.clear()
        rpolygon.pos = [70, 40, 0.]
        c.draw_visual(rpolygon)
        assert_image_equal("screenshot", 'visuals/reactive_rpolygon1.png')

        gloo.clear()
        rpolygon.radius = 25
        c.draw_visual(rpolygon)
        assert_image_equal("screenshot", 'visuals/reactive_rpolygon2.png')

        gloo.clear()
        rpolygon.color = 'red'
        c.draw_visual(rpolygon)
        assert_image_equal("screenshot", 'visuals/reactive_rpolygon3.png')

        gloo.clear()
        rpolygon.border_color = 'yellow'
        c.draw_visual(rpolygon)
        assert_image_equal("screenshot", 'visuals/reactive_rpolygon4.png')

        gloo.clear()
        rpolygon.sides = 6
        c.draw_visual(rpolygon)
        assert_image_equal("screenshot", 'visuals/reactive_rpolygon5.png')
