# -*- coding: utf-8 -*-

"""
Tests for RectPolygonVisual
All images are of size (100,100) to keep a small file size
"""

from vispy import gloo
from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, assert_image_equal,
                           TestingCanvas)
from nose.tools import assert_raises


@requires_application()
def test_rectangle_draw():
    """Test drawing rectpolygons without transform using RectPolygonVisual"""
    with TestingCanvas() as c:
        rectpolygon = visuals.RectPolygon(pos=(50, 50, 0), height=40.,
                                          width=80., color='red')
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/rectpolygon1.png')

        gloo.clear()
        rectpolygon = visuals.RectPolygon(pos=(50, 50, 0), height=40.,
                                          width=80., radius=10.,
                                          color='red')
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/rectpolygon2.png')

        gloo.clear()
        rectpolygon = visuals.RectPolygon(pos=(50, 50, 0), height=40.,
                                          width=80., radius=10.,
                                          color='red',
                                          border_color=(0, 1, 1, 1))
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/rectpolygon3.png')

        gloo.clear()
        rectpolygon = visuals.RectPolygon(pos=(50, 50, 0), height=40.,
                                          width=80., radius=10.,
                                          border_color='white')
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/rectpolygon4.png')

        gloo.clear()
        rectpolygon = visuals.RectPolygon(pos=(50, 50, 0), height=60.,
                                          width=80., radius=[25, 10, 0, 15],
                                          color='red',
                                          border_color=(0, 1, 1, 1))
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/rectpolygon5.png')


@requires_application()
def test_rectpolygon_draw():
    """Test drawing transformed rectpolygons using RectPolygonVisual"""
    with TestingCanvas() as c:
        rectpolygon = visuals.RectPolygon(pos=(0., 0.), height=20.,
                                          width=20., radius=10.,
                                          color='blue')
        rectpolygon.transform = transforms.STTransform(scale=(2.0, 3.0),
                                                       translate=(50, 50))
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/rectpolygon6.png')

        gloo.clear()
        rectpolygon = visuals.RectPolygon(pos=(0., 0.), height=20.,
                                          width=20., radius=10.,  
                                          color='blue',
                                          border_color='red')
        rectpolygon.transform = transforms.STTransform(scale=(2.0, 3.0),
                                                       translate=(50, 50))
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/rectpolygon7.png')

        gloo.clear()
        rectpolygon = visuals.RectPolygon(pos=(0., 0.), height=60.,
                                          width=60., radius=10.,
                                          border_color='red')
        rectpolygon.transform = transforms.STTransform(scale=(1.5, 0.5),
                                                       translate=(50, 50))
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/rectpolygon8.png')

        gloo.clear()
        rectpolygon = visuals.RectPolygon(pos=(0., 0.), height=60.,
                                          width=60., radius=[25, 10, 0, 15],
                                          color='blue',
                                          border_color='red')
        rectpolygon.transform = transforms.STTransform(scale=(1.5, 0.5),
                                                       translate=(50, 50))
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/rectpolygon9.png')


@requires_application()
def test_reactive_draw():
    """Test reactive RectPolygon attributes"""
    with TestingCanvas() as c:
        rectpolygon = visuals.RectPolygon(pos=(50, 50, 0), height=40.,
                                          width=80., color='red')
        c.draw_visual(rectpolygon)

        gloo.clear()
        rectpolygon.radius = [20., 20, 0., 10.]
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/reactive_rectpolygon1.png')

        gloo.clear()
        rectpolygon.pos = (60, 60, 0)
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/reactive_rectpolygon2.png')

        gloo.clear()
        rectpolygon.color = 'blue'
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/reactive_rectpolygon3.png')

        gloo.clear()
        rectpolygon.border_color = 'yellow'
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/reactive_rectpolygon4.png')

        gloo.clear()
        rectpolygon.radius = 10.
        c.draw_visual(rectpolygon)
        assert_image_equal("screenshot", 'visuals/reactive_rectpolygon5.png')


@requires_application()
def test_attributes():
    """Test if attribute checks are in place"""
    with TestingCanvas():
        rectpolygon = visuals.RectPolygon(pos=(50, 50, 0), height=40.,
                                          width=80., color='red')
        assert_raises(ValueError, setattr, rectpolygon, 'height', 0.)
        assert_raises(ValueError, setattr, rectpolygon, 'width', 0.)
        assert_raises(ValueError, setattr, rectpolygon, 'radius', [10, 0, 5])
        assert_raises(ValueError, setattr, rectpolygon, 'radius', [10.])
        assert_raises(ValueError, setattr, rectpolygon, 'radius', 21.)
