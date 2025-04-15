# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Tests for GridLines
"""

import numpy as np

from vispy.scene import GridLines, STTransform
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)


@requires_application()
def test_gridlines():
    with TestingCanvas(size=(80, 80)) as c:
        grid = GridLines(parent=c.scene)
        grid.transform = STTransform(translate=(40, 40))
        render = c.render()
        np.testing.assert_array_equal(render[40, 40], (151, 151, 151, 255))
        np.testing.assert_array_equal(render[50, 50], (0, 0, 0, 255))

        grid.grid_bounds = (-10, 10, -10, 10)
        render = c.render()
        np.testing.assert_array_equal(render[50, 50], (255, 255, 255, 255))


run_tests_if_main()
