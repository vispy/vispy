# -*- coding: utf-8 -*-

"""
Tests for EllipseVisual
All images are of size (100,100) to keep a small file size
"""

from vispy import gloo
from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, assert_image_equal,
                           requires_img_lib, TestingCanvas)


@requires_application()
@requires_img_lib()
def test_circle_draw():
    """Test drawing circles without transform using EllipseVisual"""
    with TestingCanvas():
        ellipse = visuals.Ellipse(pos=(0.5, 0.3, 0), radius=0.4,
                                  color=(1, 0, 0, 1))
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/circle1.png')

        gloo.clear()
        ellipse = visuals.Ellipse(pos=(0.5, 0.3, 0), radius=0.4,
                                  color=(1, 0, 0, 1),
                                  border_color=(0, 1, 1, 1))
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/circle2.png')

        gloo.clear()
        ellipse = visuals.Ellipse(pos=(0.5, 0.3, 0), radius=0.4,
                                  border_color=(0, 1, 1, 1))
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/circle3.png')


@requires_application()
@requires_img_lib()
def test_ellipse_draw():
    """Test drawing transformed ellipses using EllipseVisual"""
    with TestingCanvas():
        ellipse = visuals.Ellipse(pos=(0., 0.), radius=(0.4, 0.3),
                                  color=(0, 0, 1, 1))
        ellipse.transform = transforms.STTransform(scale=(2.0, 3.0))
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/ellipse1.png')

        gloo.clear()
        ellipse = visuals.Ellipse(pos=(0., 0.), radius=(0.4, 0.3),
                                  color=(0, 0, 1, 1),
                                  border_color=(1, 0, 0, 1))
        ellipse.transform = transforms.STTransform(scale=(2.0, 3.0))
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/ellipse2.png')

        gloo.clear()
        ellipse = visuals.Ellipse(pos=(0., 0.), radius=(0.4, 0.3),
                                  border_color=(1, 0, 0, 1))
        ellipse.transform = transforms.STTransform(scale=(2.0, 3.0))
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/ellipse3.png')


@requires_application()
@requires_img_lib()
def test_arc_draw1():
    """Test drawing arcs using EllipseVisual"""
    with TestingCanvas():
        ellipse = visuals.Ellipse(pos=(0., 0.), radius=(0.4, 0.3),
                                  start_angle=90., span_angle=120.,
                                  color=(0, 0, 1, 1))
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/arc1.png')

        gloo.clear()
        ellipse = visuals.Ellipse(pos=(0., 0.), radius=(0.4, 0.3),
                                  start_angle=90., span_angle=120.,
                                  border_color=(1, 0, 0, 1))
        ellipse.draw()
        assert_image_equal("screenshot", 'visuals/arc2.png')
