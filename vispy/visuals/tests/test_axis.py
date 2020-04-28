# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
Tests for AxisVisual
"""

from numpy.testing import assert_allclose

from vispy import scene
from vispy.scene import visuals
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)


@requires_application()
def test_axis():
    with TestingCanvas() as c:
        axis = visuals.Axis(pos=[[-1.0, 0], [1.0, 0]], parent=c.scene)
        c.draw_visual(axis)


@requires_application()
def test_axis_zero_domain():
    # Regression test for a bug that caused an overflow error when the domain
    # min was same as max
    with TestingCanvas() as c:
        axis = visuals.Axis(pos=[[-1.0, 0], [1.0, 0]], domain=(0.5, 0.5), parent=c.scene)
        c.draw_visual(axis)


@requires_application()
def test_rotation_angle():

    # Make sure the rotation angle calculation is correct

    canvas = scene.SceneCanvas(keys=None, size=(800, 600), show=True)
    view = canvas.central_widget.add_view()
    view.camera = scene.cameras.TurntableCamera(parent=view.scene,
                                                fov=0., distance=4.0,
                                                elevation=0, azimuth=0, roll=0.)

    axis1 = visuals.Axis(pos=[[-1.0, 0], [1.0, 0]], parent=view.scene)
    assert_allclose(axis1._rotation_angle, 0)

    axis2 = visuals.Axis(pos=[[-3**0.5/2., -0.5], [3**0.5/2., 0.5]], parent=view.scene)
    assert_allclose(axis2._rotation_angle, 0.)

    view.camera.elevation = 90.

    assert_allclose(axis1._rotation_angle, 0)
    assert_allclose(axis2._rotation_angle, -30)

    view.camera.elevation = 45.

    assert_allclose(axis1._rotation_angle, 0)
    assert_allclose(axis2._rotation_angle, -22.207653)

    view.camera.fov = 20.

    assert_allclose(axis1._rotation_angle, 0)
    # OSX Travis has some small differences...sometimes
    assert_allclose(axis2._rotation_angle, -17.056795, rtol=0.05)


run_tests_if_main()
