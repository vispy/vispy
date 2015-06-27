# -*- coding: utf-8 -*-

"""
Tests for RectPolygonVisual
All images are of size (100,100) to keep a small file size
"""

from vispy.scene import visuals, transforms
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main, raises)
from vispy.testing.image_tester import assert_image_approved


@requires_application()
def test_rectangle_draw():
    """Test drawing rectpolygons without transform using RectPolygonVisual"""
    with TestingCanvas() as c:
        rectpolygon = visuals.Rectangle(center=(50, 50, 0), height=40.,
                                        width=80., color='red',
                                        parent=c.scene)

        assert_image_approved(c.render(), 'visuals/rectpolygon1.png')

        rectpolygon.parent = None
        rectpolygon = visuals.Rectangle(center=(50, 50, 0), height=40.,
                                        width=80., radius=10., color='red',
                                        parent=c.scene)

        assert_image_approved(c.render(), 'visuals/rectpolygon2.png')

        rectpolygon.parent = None
        rectpolygon = visuals.Rectangle(center=(50, 50, 0), height=40.,
                                        width=80., radius=10., color='red',
                                        border_color=(0, 1, 1, 1),
                                        parent=c.scene)

        assert_image_approved(c.render(), 'visuals/rectpolygon3.png')

        rectpolygon.parent = None
        rectpolygon = visuals.Rectangle(center=(50, 50, 0), height=40.,
                                        width=80., radius=10.,
                                        border_color='white',
                                        parent=c.scene)

        assert_image_approved(c.render(), 'visuals/rectpolygon4.png',
                              min_corr=0.5)

        rectpolygon.parent = None
        rectpolygon = visuals.Rectangle(center=(50, 50, 0), height=60.,
                                        width=80., radius=[25, 10, 0, 15],
                                        color='red', border_color=(0, 1, 1, 1),
                                        parent=c.scene)

        assert_image_approved(c.render(), 'visuals/rectpolygon5.png')


@requires_application()
def test_rectpolygon_draw():
    """Test drawing transformed rectpolygons using RectPolygonVisual"""
    with TestingCanvas() as c:
        rectpolygon = visuals.Rectangle(center=(0., 0.), height=20.,
                                        width=20., radius=10., color='blue',
                                        parent=c.scene)
        rectpolygon.transform = transforms.STTransform(scale=(2.0, 3.0),
                                                       translate=(50, 50))

        assert_image_approved(c.render(), 'visuals/rectpolygon6.png')

        rectpolygon.parent = None
        rectpolygon = visuals.Rectangle(center=(0., 0.), height=20.,
                                        width=20., radius=10.,
                                        color='blue', border_color='red',
                                        parent=c.scene)
        rectpolygon.transform = transforms.STTransform(scale=(2.0, 3.0),
                                                       translate=(50, 50))

        assert_image_approved(c.render(), 'visuals/rectpolygon7.png')

        rectpolygon.parent = None
        rectpolygon = visuals.Rectangle(center=(0., 0.), height=60.,
                                        width=60., radius=10.,
                                        border_color='red',
                                        parent=c.scene)
        rectpolygon.transform = transforms.STTransform(scale=(1.5, 0.5),
                                                       translate=(50, 50))

        assert_image_approved(c.render(), 'visuals/rectpolygon8.png',
                              min_corr=0.5)

        rectpolygon.parent = None
        rectpolygon = visuals.Rectangle(center=(0., 0.), height=60.,
                                        width=60., radius=[25, 10, 0, 15],
                                        color='blue', border_color='red',
                                        parent=c.scene)
        rectpolygon.transform = transforms.STTransform(scale=(1.5, 0.5),
                                                       translate=(50, 50))

        assert_image_approved(c.render(), 'visuals/rectpolygon9.png')


@requires_application()
def test_reactive_draw():
    """Test reactive RectPolygon attributes"""
    with TestingCanvas() as c:
        rectpolygon = visuals.Rectangle(center=(50, 50, 0), height=40.,
                                        width=80., color='red',
                                        parent=c.scene)

        rectpolygon.radius = [20., 20, 0., 10.]

        assert_image_approved(c.render(),
                              'visuals/reactive_rectpolygon1.png')

        rectpolygon.center = (60, 60, 0)

        assert_image_approved(c.render(),
                              'visuals/reactive_rectpolygon2.png')

        rectpolygon.color = 'blue'

        assert_image_approved(c.render(),
                              'visuals/reactive_rectpolygon3.png')

        rectpolygon.border_color = 'yellow'

        assert_image_approved(c.render(),
                              'visuals/reactive_rectpolygon4.png')

        rectpolygon.radius = 10.

        assert_image_approved(c.render(),
                              'visuals/reactive_rectpolygon5.png')


@requires_application()
def test_attributes():
    """Test if attribute checks are in place"""
    with TestingCanvas() as c:
        rectpolygon = visuals.Rectangle(center=(50, 50, 0), height=40.,
                                        width=80., color='red',
                                        parent=c.scene)
        with raises(ValueError):
            rectpolygon.height = 0
        with raises(ValueError):
            rectpolygon.width = 0
        with raises(ValueError):
            rectpolygon.radius = [10, 0, 5]
        with raises(ValueError):
            rectpolygon.radius = [10.]
        with raises(ValueError):
            rectpolygon.radius = 21.


run_tests_if_main()
