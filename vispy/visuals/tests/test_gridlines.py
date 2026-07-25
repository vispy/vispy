# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Tests for GridLines
"""

import numpy as np

from vispy.scene import GridLines, STTransform, Rectangle, MatrixTransform
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


@requires_application()
def test_gridlines_depth():
    with TestingCanvas(size=(80, 80)) as c:
        view = c.central_widget.add_view() 
        view.camera = 'arcball'

        # create a grid and a rectangle; the rect is closed to the camera an should
        # hide the grid if the depth tests are working
        rect = Rectangle(center=(0, 0, 0), height=20, width=20, color='white', parent=view.scene)
        rect.transform = MatrixTransform()
        rect.transform.rotate(90, (1, 0, 0))
        rect.transform.translate((0, -1, 0))

        grid = GridLines(color='red', parent=view.scene)
        grid.transform = MatrixTransform()
        grid.transform.rotate(90, (1, 0, 0))

        # translucent preset to ensure depth test
        grid.update_gl_state(preset='translucent')
        rect.update_gl_state(preset='translucent')

        render = c.render()

        # should be all white
        np.testing.assert_array_equal(render[40, 40], (255, 255, 255, 255))
        np.testing.assert_array_equal(render[45, 45], (255, 255, 255, 255))

        # move the rect behind, we should now see the grid
        rect.transform.translate((0, 2, 0))
        render = c.render()

        # not pure red in the render due to interpolation, but should be non-white
        np.testing.assert_array_equal(render[40, 40], (255, 104, 104, 255))
        np.testing.assert_array_equal(render[45, 45], (255, 255, 255, 255))

        render = c.render()
        np.testing.assert_array_equal(render[50, 50], (255, 255, 255, 255))


run_tests_if_main()
