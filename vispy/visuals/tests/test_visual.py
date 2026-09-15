# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Tests for BaseVisual, CompoundVisual, and Visual views."""

import numpy as np

from vispy.visuals import LineVisual, LinePlotVisual
from vispy.testing import run_tests_if_main


def test_line_bounds_invalidation():
    line = LineVisual()
    line.set_data(pos=np.array([[0., 0.], [1., 1.]]))
    assert line.bounds(0) == (0., 1.)
    line.set_data(pos=np.array([[0., 0.], [100., 100.]]))
    assert line.bounds(0) == (0., 100.)


def test_compound_lineplot_bounds_invalidation():
    plot = LinePlotVisual((np.array([0., 1.]), np.array([0., 1.])))
    assert tuple(plot.bounds(1)) == (0., 1.)
    plot.set_data((np.array([0., 1.]), np.array([0., 100.])))
    assert tuple(plot.bounds(1)) == (0., 100.)


def test_subvisual_change_invalidates_compound():
    # Changing the data of a subvisual directly must invalidate the
    # aggregated bounds of the enclosing compound visual.
    plot = LinePlotVisual((np.array([0., 1.]), np.array([0., 1.])))
    assert tuple(plot.bounds(1)) == (0., 1.)
    plot._line.set_data(pos=np.array([[0., 0.], [1., 500.]]))
    assert tuple(plot.bounds(1)) == (0., 500.)


def test_view_bounds_return_value():
    # BaseVisualView._compute_bounds must forward the computed bounds
    # (a missing `return` made views report None).
    line = LineVisual()
    line.set_data(pos=np.array([[0., 0.], [1., 1.]]))
    view = line.view()
    assert view.bounds(0) == (0., 1.)


def test_view_bounds_invalidated_after_set_data():
    # Views share the visual's data, so bounds of a view must be
    # invalidated when the base visual's data changes.
    line = LineVisual()
    line.set_data(pos=np.array([[0., 0.], [1., 1.]]))
    view = line.view()
    assert view.bounds(1) == (0., 1.)
    line.set_data(pos=np.array([[0., 0.], [1., 777.]]))
    assert view.bounds(1) == (0., 777.)


def test_bounds_change_event():
    # The `bounds_change` event (declared on all visuals) must be emitted
    # when the bounds may have changed.
    line = LineVisual()
    line.set_data(pos=np.array([[0., 0.], [1., 1.]]))
    n_events = [0]
    line.events.bounds_change.connect(lambda ev: n_events.__setitem__(0, n_events[0] + 1))
    line.set_data(pos=np.array([[0., 0.], [10., 10.]]))
    assert n_events[0] == 1
    # data changes that cannot affect bounds do not emit the event
    line.set_data(color='red')
    assert n_events[0] == 1


run_tests_if_main()
