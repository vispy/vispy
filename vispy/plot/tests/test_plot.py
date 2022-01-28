# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import vispy.plot as vp
from vispy.testing import (assert_raises, requires_application,
                           run_tests_if_main)
from vispy.visuals.axis import AxisVisual
from unittest import mock
from vispy import scene, app
import numpy as np


@requires_application()
def test_figure_creation():
    """Test creating a figure"""
    with vp.Fig(show=False) as fig:
        fig[0, 0:2]
        fig[1:3, 0:2]
        ax_right = fig[1:3, 2]
        assert fig[1:3, 2] is ax_right
        # collision
        assert_raises(ValueError, fig.__getitem__, (slice(1, 3), 1))


@requires_application()
def test_plot_widget_axes():
    """Test that the axes domains are updated correctly when a figure is first drawn"""
    fig = vp.Fig(size=(800, 800), show=False)
    point = (0, 100)
    fig[0, 0].plot((point, point))
    # mocking the AxisVisual domain.setter
    domain_setter = mock.Mock(wraps=AxisVisual.domain.fset)
    mock_property = AxisVisual.domain.setter(domain_setter)

    with mock.patch.object(AxisVisual, "domain", mock_property):
        # note: fig.show() must be called for this test to work... otherwise
        # Grid._update_child_widget_dim is not triggered and the axes aren't updated
        fig.show(run=False)
        # currently, the AxisWidget adds a buffer of 5% of the
        # full range to either end of the axis domain
        buffer = (point[1] - point[0]) * 0.05
        expectation = [point[0] - buffer, point[1] + buffer]
        for call in domain_setter.call_args_list:
            assert [round(x, 2) for x in call[0][1]] == expectation


@requires_application()
def test_bar_creation():
    """Test creating a figure"""

    canvas = scene.SceneCanvas(keys='interactive', vsync=False)
    canvas.size = 800, 600
    canvas.show()

    grid = canvas.central_widget.add_grid()
    grid.padding = 10

    # Create two ViewBoxes, place side-by-side
    vb1 = grid.add_view(row=0, col=1, camera='panzoom')

    x_axis1 = scene.AxisWidget(orientation='bottom')
    x_axis1.stretch = (1, 0.1)
    grid.add_widget(x_axis1, row=1, col=1)
    x_axis1.link_view(vb1)
    y_axis1 = scene.AxisWidget(orientation='left')
    y_axis1.stretch = (0.1, 1)
    grid.add_widget(y_axis1, row=0, col=0)
    y_axis1.link_view(vb1)

    length = 100

    h = 10

    bottom = np.random.randint(h, size=length)

    height = bottom + np.random.randint(h, size=length)

    index = np.arange(length, dtype=int)

    scene.Bar(index=index, bottom=bottom,
              height=height, width=0.8, color=(0.25, 0.8, 0.),
              parent=vb1.scene)

    vb1.camera.set_range()

    # canvas.measure_fps()
    app.run()


run_tests_if_main()
