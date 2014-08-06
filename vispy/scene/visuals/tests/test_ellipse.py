# -*- coding: utf-8 -*-

"""
Tests for EllipseVisual
All images are of size (100,100) to keep a small file size
"""

import sys

from vispy import gloo
from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, assert_image_equal,
                           TestingCanvas, SkipTest)


@requires_application()
def test_circle_draw():
    """Test drawing circles without transform using EllipseVisual"""
    
    # TODO: remove this skip after fixing 
    # https://github.com/vispy/vispy/issues/374
    if sys.version[0] == '3':
        raise SkipTest
    
    with TestingCanvas() as c:
        ellipse = visuals.Ellipse(pos=(75, 35, 0), radius=20,
                                  color=(1, 0, 0, 1))
        c.draw_visual(ellipse)
        assert_image_equal("screenshot", 'visuals/circle1.png')

        gloo.clear()
        ellipse = visuals.Ellipse(pos=(75, 35, 0), radius=20,
                                  color=(1, 0, 0, 1),
                                  border_color=(0, 1, 1, 1))
        c.draw_visual(ellipse)
        assert_image_equal("screenshot", 'visuals/circle2.png')

        gloo.clear()
        ellipse = visuals.Ellipse(pos=(75, 35, 0), radius=20,
                                  border_color=(0, 1, 1, 1))
        c.draw_visual(ellipse)
        assert_image_equal("screenshot", 'visuals/circle3.png')


@requires_application()
def test_ellipse_draw():
    """Test drawing transformed ellipses using EllipseVisual"""
    
    # TODO: remove this skip after fixing 
    # https://github.com/vispy/vispy/issues/374
    if sys.version[0] == '3':
        raise SkipTest
    
    with TestingCanvas() as c:
        ellipse = visuals.Ellipse(pos=(0., 0.), radius=(20, 15),
                                  color=(0, 0, 1, 1))
        ellipse.transform = transforms.STTransform(scale=(2.0, 3.0),
                                                   translate=(50, 50))
        c.draw_visual(ellipse)
        assert_image_equal("screenshot", 'visuals/ellipse1.png')

        gloo.clear()
        ellipse = visuals.Ellipse(pos=(0., 0.), radius=(20, 15),
                                  color=(0, 0, 1, 1),
                                  border_color=(1, 0, 0, 1))
        ellipse.transform = transforms.STTransform(scale=(2.0, 3.0),
                                                   translate=(50, 50))
        c.draw_visual(ellipse)
        assert_image_equal("screenshot", 'visuals/ellipse2.png')

        gloo.clear()
        ellipse = visuals.Ellipse(pos=(0., 0.), radius=(20, 15),
                                  border_color=(1, 0, 0, 1))
        ellipse.transform = transforms.STTransform(scale=(2.0, 3.0),
                                                   translate=(50, 50))
        c.draw_visual(ellipse)
        assert_image_equal("screenshot", 'visuals/ellipse3.png')


@requires_application()
def test_arc_draw1():
    """Test drawing arcs using EllipseVisual"""
    
    # TODO: remove this skip after fixing 
    # https://github.com/vispy/vispy/issues/374
    if sys.version[0] == '3':
        raise SkipTest
    
    with TestingCanvas() as c:
        ellipse = visuals.Ellipse(pos=(50., 50.), radius=(20, 15),
                                  start_angle=150., span_angle=120.,
                                  color=(0, 0, 1, 1))
        c.draw_visual(ellipse)
        assert_image_equal("screenshot", 'visuals/arc1.png')

        gloo.clear()
        ellipse = visuals.Ellipse(pos=(50., 50.), radius=(20, 15),
                                  start_angle=90., span_angle=120.,
                                  border_color=(1, 0, 0, 1))
        c.draw_visual(ellipse)
        assert_image_equal("screenshot", 'visuals/arc2.png')


@requires_application()
def test_reactive_draw():
    """Test reactive ellipse attributes"""
    with TestingCanvas():
        ellipse = visuals.Ellipse(pos=[0.5, 0.3, 0.], radius=[0.4, 0.3],
                                  color='yellow')
        ellipse.draw()

        gloo.clear()
        ellipse.pos = [0.4, 0.2, 0.]
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/reactive_ellipse1.png')

        gloo.clear()
        ellipse.radius = 0.5
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/reactive_ellipse2.png')

        gloo.clear()
        ellipse.color = 'red'
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/reactive_ellipse3.png')

        gloo.clear()
        ellipse.border_color = 'yellow'
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/reactive_ellipse4.png')

        gloo.clear()
        ellipse.start_angle = 120.
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/reactive_ellipse5.png')

        gloo.clear()
        ellipse.span_angle = 100.
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/reactive_ellipse6.png')

        gloo.clear()
        ellipse.num_segments = 10.
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/reactive_ellipse7.png')
