# -*- coding: utf-8 -*-
import numpy as np
import pytest
from vispy.scene.visuals import Markers
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@requires_application()
def test_markers():
    """Test basic marker / point-sprite support"""
    # this is probably too basic, but it at least ensures that point sprites
    # work for people
    np.random.seed(57983)
    data = np.random.normal(size=(30, 2), loc=50, scale=10)

    with TestingCanvas() as c:
        marker = Markers(parent=c.scene)
        marker.set_data(data)
        assert_image_approved(c.render(), "visuals/markers.png")

    # Test good correlation at high-dpi
    with TestingCanvas(px_scale=2) as c:
        marker = Markers(parent=c.scene)
        marker.set_data(data)
        assert_image_approved(c.render(), "visuals/markers.png")


def test_markers_edge_width():
    data = np.random.rand(10, 3)
    edge_width = np.random.rand(10)
    marker = Markers()

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

run_tests_if_main()
