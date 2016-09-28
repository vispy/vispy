# -*- coding: utf-8 -*-

"""
Tests for LineVisual
"""

from vispy.scene import visuals
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)


@requires_application()
def test_line():
    with TestingCanvas() as c:
        line = visuals.Line(pos=[[-1.0, 0], [1.0, 0]])
        c.draw_visual(line)


run_tests_if_main()
