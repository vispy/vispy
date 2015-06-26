# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Tests for EllipseVisual
All images are of size (100,100) to keep a small file size
"""

from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, TestingCanvas, 
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@requires_application()
def test_circle_draw():
    """Test drawing circles without transform using EllipseVisual"""
    with TestingCanvas() as c:
        ellipse = visuals.Ellipse(center=(75, 35, 0), radius=20,
                                  color=(1, 0, 0, 1),
                                  parent=c.scene)
        assert_image_approved(c.render(), 'visuals/circle1.png')

        ellipse.parent = None
        ellipse = visuals.Ellipse(center=(75, 35, 0), radius=20,
                                  color=(1, 0, 0, 1),
                                  border_color=(0, 1, 1, 1),
                                  parent=c.scene)
        assert_image_approved(c.render(), 'visuals/circle2.png')

        ellipse.parent = None
        ellipse = visuals.Ellipse(center=(75, 35, 0), radius=20,
                                  border_color=(0, 1, 1, 1),
                                  parent=c.scene)

        # low corr here because borders have some variability
        # esp. w/HiDPI
        assert_image_approved(c.render(), 'visuals/circle3.png',
                              min_corr=0.7)


@requires_application()
def test_ellipse_draw():
    """Test drawing transformed ellipses using EllipseVisual"""
    with TestingCanvas() as c:
        ellipse = visuals.Ellipse(center=(0., 0.), radius=(20, 15),
                                  color=(0, 0, 1, 1),
                                  parent=c.scene)
        ellipse.transform = transforms.STTransform(scale=(2.0, 3.0),
                                                   translate=(50, 50))
        assert_image_approved(c.render(), 'visuals/ellipse1.png')

        ellipse.parent = None
        ellipse = visuals.Ellipse(center=(0., 0.), radius=(20, 15),
                                  color=(0, 0, 1, 1),
                                  border_color=(1, 0, 0, 1),
                                  parent=c.scene)
        ellipse.transform = transforms.STTransform(scale=(2.0, 3.0),
                                                   translate=(50, 50))
        assert_image_approved(c.render(), 'visuals/ellipse2.png')

        ellipse.parent = None
        ellipse = visuals.Ellipse(center=(0., 0.), radius=(20, 15),
                                  border_color=(1, 0, 0, 1),
                                  parent=c.scene)
        ellipse.transform = transforms.STTransform(scale=(2.0, 3.0),
                                                   translate=(50, 50))
        assert_image_approved(c.render(), 'visuals/ellipse3.png',
                              min_corr=0.7)


@requires_application()
def test_arc_draw1():
    """Test drawing arcs using EllipseVisual"""
    with TestingCanvas() as c:
        ellipse = visuals.Ellipse(center=(50., 50.), radius=(20, 15),
                                  start_angle=150., span_angle=120.,
                                  color=(0, 0, 1, 1),
                                  parent=c.scene)
        assert_image_approved(c.render(), 'visuals/arc1.png')

        ellipse.parent = None
        ellipse = visuals.Ellipse(center=(50., 50.), radius=(20, 15),
                                  start_angle=150., span_angle=120.,
                                  border_color=(1, 0, 0, 1),
                                  parent=c.scene)
        assert_image_approved(c.render(), 'visuals/arc2.png',
                              min_corr=0.6)


@requires_application()
def test_reactive_draw():
    """Test reactive ellipse attributes"""
    with TestingCanvas() as c:
        ellipse = visuals.Ellipse(center=[75, 35, 0.], radius=[20, 15],
                                  color='yellow',
                                  parent=c.scene)

        ellipse.center = [70, 40, 0.]
        assert_image_approved(c.render(), 'visuals/reactive_ellipse1.png')

        ellipse.radius = 25
        assert_image_approved(c.render(), 'visuals/reactive_ellipse2.png')

        ellipse.color = 'red'
        assert_image_approved(c.render(), 'visuals/reactive_ellipse3.png')

        ellipse.border_color = 'yellow'
        assert_image_approved(c.render(), 'visuals/reactive_ellipse4.png')

        ellipse.start_angle = 140.
        assert_image_approved(c.render(), 'visuals/reactive_ellipse5.png')

        ellipse.span_angle = 100.
        assert_image_approved(c.render(), 'visuals/reactive_ellipse6.png')

        ellipse.num_segments = 10.
        assert_image_approved(c.render(), 'visuals/reactive_ellipse7.png')


run_tests_if_main()
