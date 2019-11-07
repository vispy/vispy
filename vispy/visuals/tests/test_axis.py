# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
Tests for AxisVisual
"""

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


run_tests_if_main()
