# -*- coding: utf-8 -*-
import numpy as np
import pytest
from vispy.gloo.gl import use_gl
from vispy.scene.visuals import Markers
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@pytest.fixture(params=['points', 'instanced'])
def rendering_method(request):
    """Skip test if instanced rendering is requested but gl+ backend is unavailable."""
    method = request.param
    try:
        use_gl('gl+' if method == 'instanced' else 'gl2')
        yield method
    except Exception:
        pytest.skip("gl+ backend not available for instanced rendering test")
    finally:
        use_gl('gl2')


@requires_application()
def test_markers(rendering_method):
    """Test basic marker / point-sprite support"""
    # this is probably too basic, but it at least ensures that point sprites
    # work for people
    np.random.seed(57983)
    data = np.random.normal(size=(30, 2), loc=50, scale=10)

    with TestingCanvas() as c:
        marker = Markers(parent=c.scene, method=rendering_method)
        marker.set_data(data)
        assert_image_approved(c.render(), "visuals/markers.png")

    # Test good correlation at high-dpi
    with TestingCanvas(px_scale=2) as c:
        marker = Markers(parent=c.scene, method=rendering_method)
        marker.set_data(data)
        assert_image_approved(c.render(), "visuals/markers.png")


@pytest.mark.parametrize('method', ['points', 'instanced'])
def test_markers_edge_width(method):
    data = np.random.rand(10, 3)
    edge_width = np.random.rand(10)
    marker = Markers(method=method)

    with pytest.raises(ValueError):
        marker.set_data(pos=data, edge_width_rel=1, edge_width=1)

    marker.set_data(pos=data, edge_width=2)
    marker.set_data(pos=data, edge_width=edge_width)
    with pytest.raises(ValueError):
        marker.set_data(pos=data, edge_width=-1)

    marker.set_data(pos=data, edge_width_rel=edge_width, edge_width=None)
    marker.set_data(pos=data, edge_width_rel=edge_width + 1, edge_width=None)
    with pytest.raises(ValueError):
        marker.set_data(pos=data, edge_width_rel=edge_width - 1, edge_width=None)


@pytest.mark.parametrize('method', ['points', 'instanced'])
def test_empty_markers_symbol(method):
    markers = Markers(method=method)
    markers.symbol = 'o'


def test_markers_method_parameter():
    """Test that method parameter is validated and works correctly."""
    data = np.random.rand(10, 3)

    markers_points = Markers(method='points')
    markers_points.set_data(pos=data)
    assert markers_points._method == 'points'
    assert markers_points._draw_mode == 'points'

    markers_instanced = Markers(method='instanced')
    markers_instanced.set_data(pos=data)
    assert markers_instanced._method == 'instanced'
    assert markers_instanced._draw_mode == 'triangles'

    with pytest.raises(ValueError, match="method must be 'points' or 'instanced'"):
        Markers(method='invalid')


@pytest.mark.parametrize('method', ['points', 'instanced'])
def test_markers_empty_data(method):
    """Test that setting empty data (not None) doesn't crash and clears existing data."""
    data = np.random.rand(10, 3)

    empty_pos = np.array([]).reshape(0, 2)

    markers = Markers(method=method)
    markers.set_data(pos=empty_pos)  # Should not crash
    assert markers._data is None  # Should be None with empty data

    markers.set_data(pos=data)
    assert markers._data is not None  # Should have data now

    markers.set_data(pos=empty_pos)
    assert markers._data is None  # Should be cleared

    markers.set_data(pos=data)
    assert markers._data is not None

    markers.set_data(pos=None)
    assert markers._data is None  # Should be cleared


@pytest.mark.parametrize('method', ['points', 'instanced'])
def test_markers_canvas_size_limits(method):
    """Test canvas size clamping feature."""
    data = np.random.rand(10, 3)
    markers = Markers(method=method)

    # default None (no clamping)
    assert markers.canvas_size_limits is None

    markers.canvas_size_limits = (5, 100)
    assert markers.canvas_size_limits == (5, 100)

    markers.set_data(pos=data)

    markers.canvas_size_limits = (None, 100)  # Only max
    assert markers.canvas_size_limits == (None, 100)

    markers.canvas_size_limits = (5, None)  # Only min
    assert markers.canvas_size_limits == (5, None)

    with pytest.raises(ValueError, match="tuple of \\(min, max\\)"):
        markers.canvas_size_limits = 10  # Not a tuple

    with pytest.raises(ValueError, match="tuple of \\(min, max\\)"):
        markers.canvas_size_limits = (10,)  # Wrong length

    with pytest.raises(ValueError, match="non-negative"):
        markers.canvas_size_limits = (-5, 100)  # Negative min

    with pytest.raises(ValueError, match="non-negative"):
        markers.canvas_size_limits = (5, -100)  # Negative max

    with pytest.raises(ValueError, match="min must be <= max"):
        markers.canvas_size_limits = (100, 50)  # Min > max

    # can be set back to None
    markers.canvas_size_limits = None
    assert markers.canvas_size_limits is None


run_tests_if_main()
