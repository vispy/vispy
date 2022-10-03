# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""Tests for AxisVisual"""

from numpy.testing import assert_allclose, assert_array_equal

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
    assert_allclose(axis2._rotation_angle, -30, rtol=1e-3)

    view.camera.elevation = 45.

    assert_allclose(axis1._rotation_angle, 0)
    assert_allclose(axis2._rotation_angle, -22.207653, rtol=1e-3)

    view.camera.fov = 20.

    assert_allclose(axis1._rotation_angle, 0)
    # OSX Travis has some small differences...sometimes
    assert_allclose(axis2._rotation_angle, -17.056795, rtol=0.05)


@requires_application()
def test_text_position():

    # Test the labels text and position of the axis depending on its domain

    canvas = scene.SceneCanvas(keys=None, size=(800, 600), show=True)
    view = canvas.central_widget.add_view()
    view.camera = scene.cameras.PanZoomCamera(parent=view.scene)

    # tick length and label margin to 0 for nice values
    axis1 = visuals.Axis(pos=[[-1.0, 0], [1.0, 0]], domain=(0., 1.25), 
                         major_tick_length=0, tick_label_margin=0, 
                         parent=view.scene)

    canvas.draw_visual(axis1)
    assert_allclose(axis1._text.pos[:, 0], (-1, -0.2, 0.6))
    assert_array_equal(axis1._text.text, ('0', '0.5', '1'))

    # Flip the axis domain
    axis1.domain = (1.25, 0.)
    canvas.draw_visual(axis1)
    # Text should be unchanged and positions mirrored
    assert_allclose(axis1._text.pos[:, 0], (1, 0.2, -0.6))
    assert_array_equal(axis1._text.text, ('0', '0.5', '1'))


@requires_application()
def test_tick_position():

    # Test the position of the ticks depending on the axis domain

    canvas = scene.SceneCanvas(keys=None, size=(800, 600), show=True)
    view = canvas.central_widget.add_view()
    view.camera = scene.cameras.PanZoomCamera(parent=view.scene)

    axis1 = visuals.Axis(pos=[[-1.0, 0], [1.0, 0]], domain=(0., 1.25), parent=view.scene)

    canvas.draw_visual(axis1)
    # Get a nice array of x ticks positions
    x_ticks_positions = axis1._ticks.pos[::2, ::2].flatten()
    # Compare major ticks first
    assert_allclose(x_ticks_positions[:3], (-1, -0.2, 0.6))
    # Then minor ticks
    assert_allclose(x_ticks_positions[3:], (-0.84, -0.68, -0.52, -0.36, -0.04, 0.12, 0.28, 0.44, 0.76, 0.92))

    # Flip the axis domain
    axis1.domain = (1.25, 0.)
    canvas.draw_visual(axis1)
    x_ticks_positions = axis1._ticks.pos[::2, ::2].flatten()
    # Positions should be mirrored
    assert_allclose(x_ticks_positions[:3], (1, 0.2, -0.6))
    assert_allclose(x_ticks_positions[3:], (0.84, 0.68, 0.52, 0.36, 0.04, -0.12, -0.28, -0.44, -0.76, -0.92))

run_tests_if_main()
