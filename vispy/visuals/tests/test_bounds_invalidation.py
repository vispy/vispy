# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Tests that visual bounds are invalidated when data changes.

When ``set_data`` (or an equivalent data-mutating method/property) is called,
the cached bounds of the visual must be cleared so that subsequent calls to
``bounds()`` (e.g. from ``camera.set_range``) return up-to-date values.

See https://github.com/vispy/vispy/issues/1899
"""

import numpy as np

from vispy.visuals import (LineVisual, MarkersVisual, ImageVisual,
                           MeshVisual, VolumeVisual, TextVisual,
                           InfiniteLineVisual, LinearRegionVisual,
                           WindbarbVisual, LinePlotVisual)


def test_line_bounds_invalidation():
    line = LineVisual()
    line.set_data(pos=np.array([[0., 0.], [1., 1.]]))
    assert line.bounds(0) == (0., 1.)
    line.set_data(pos=np.array([[0., 0.], [100., 100.]]))
    assert line.bounds(0) == (0., 100.)


def test_markers_bounds_invalidation():
    markers = MarkersVisual()
    markers.set_data(pos=np.array([[0., 0.], [1., 1.]]))
    assert markers.bounds(1) == (0., 1.)
    markers.set_data(pos=np.array([[0., 0.], [200., 200.]]))
    assert markers.bounds(1) == (0., 200.)


def test_image_bounds_invalidation():
    # This is the scenario of issue #1899: set_range() does not respect
    # image resizing after set_data is called with differently-shaped data.
    image = ImageVisual(np.zeros((10, 10), dtype=np.float32))
    assert image.bounds(0) == (0, 10)
    assert image.bounds(1) == (0, 10)
    image.set_data(np.zeros((100, 50), dtype=np.float32))
    assert image.bounds(0) == (0, 50)
    assert image.bounds(1) == (0, 100)


def test_mesh_bounds_invalidation():
    verts = np.array([[0., 0., 0.], [1., 1., 1.]], dtype=np.float32)
    faces = np.array([[0, 1, 0]], dtype=np.uint32)
    mesh = MeshVisual(vertices=verts, faces=faces)
    assert mesh.bounds(0) == (0., 1.)
    mesh.set_data(vertices=np.array([[0., 0., 0.], [42., 42., 42.]],
                                    dtype=np.float32),
                  faces=faces)
    assert mesh.bounds(0) == (0., 42.)


def test_volume_bounds_invalidation():
    vol = VolumeVisual(np.zeros((5, 5, 5), dtype=np.float32))
    assert vol.bounds(0) == (0, 5)
    vol.set_data(np.zeros((50, 50, 50), dtype=np.float32))
    assert vol.bounds(0) == (0, 50)


def test_text_bounds_invalidation():
    text = TextVisual('hello', pos=(5, 5))
    assert text.bounds(0) == (5, 5)
    text.pos = (90, 5)
    assert text.bounds(0) == (90, 90)


def test_infinite_line_bounds_invalidation():
    line = InfiniteLineVisual(pos=3., vertical=True)
    assert line.bounds(0) == (3., 3.)
    line.set_data(pos=17.)
    assert line.bounds(0) == (17., 17.)


def test_linear_region_bounds_invalidation():
    region = LinearRegionVisual(pos=(2, 4), vertical=True)
    assert region.bounds(0) == (2, 4)
    region.set_data(pos=(10, 20))
    assert region.bounds(0) == (10, 20)


def test_windbarb_bounds_invalidation():
    pos = np.array([[0., 0.]])
    wind = np.array([[5., 3.]])
    barbs = WindbarbVisual(pos=pos, wind=wind)
    assert barbs.bounds(0) == (0., 0.)
    barbs.set_data(pos=np.array([[9., 9.]]), wind=wind)
    assert barbs.bounds(0) == (9., 9.)


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
