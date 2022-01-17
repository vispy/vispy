# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import vispy.plot as vp
from vispy.testing import (assert_raises, requires_application,
                           run_tests_if_main)
from vispy.visuals.axis import AxisVisual
from unittest import mock


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


run_tests_if_main()
