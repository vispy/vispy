# -*- coding: utf-8 -*-

"""
Tests for AxisVisual
"""

from vispy.scene import visuals
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)


@requires_application()
def test_colorbar_draw():
    """Test drawing Colorbar without transform using ColorbarVisual"""
    with TestingCanvas() as c:
        axis = visuals.Axis(pos=[[-1.0, 0], [1.0, 0]])
        c.draw_visual(axis)


run_tests_if_main()
