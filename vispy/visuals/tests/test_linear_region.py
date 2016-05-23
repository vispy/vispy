# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Tests for LinearRegionVisual
All images are of size (100,100) to keep a small file size
"""

import numpy as np

from vispy.scene import visuals
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved
from vispy.testing import assert_raises


@requires_application()
def test_linear_region_vertical_horizontal():
    """Test vertical and horizontal LinearRegionVisual with a single color"""

    # Definition of the region
    pos = np.array([5, 15, 24, 36, 40, 42], dtype=np.float32)
    # Expected internal pos buffer for vertical region
    expected_pos_v = np.array([[5.0, -1.],
                               [5.0, 1.],
                               [15.0, -1.],
                               [15.0, 1.],
                               [24.0, -1.],
                               [24.0, 1.],
                               [36.0, -1.],
                               [36.0, 1.],
                               [40.0, -1.],
                               [40.0, 1.],
                               [42.0, -1.],
                               [42.0, 1.]], dtype=np.float32)
    # Expected internal pos buffer for horizontal region
    expected_pos_h = np.array([expected_pos_v[:, 1] * -1,
                               expected_pos_v[:, 0]], dtype=np.float32).T

    # Test both horizontal and vertical region
    for is_vertical, reference_image in [(True, 'linear_region1.png'),
                                         (False, 'linear_region1_h.png')]:

        expected_pos = expected_pos_v if is_vertical else expected_pos_h

        with TestingCanvas() as c:
            # Check set_data is working correctly within visual constructor
            region = visuals.LinearRegion(pos=pos,
                                          color=[0.0, 1.0, 0.0, 0.5],
                                          vertical=is_vertical,
                                          parent=c.scene)
            assert np.all(region._pos == expected_pos)
            assert np.all(region.pos == pos)
            assert region.is_vertical == is_vertical

            # Check set_data is working as expected when passing a list as
            # pos argument
            region.set_data(pos=list(pos))
            assert np.all(region._pos == expected_pos)
            assert np.all(region.pos == pos)

            # Check set_data is working as expected when passing a tuple as
            # pos argument
            region.set_data(pos=tuple(pos))
            assert np.all(region._pos == expected_pos)
            assert np.all(region.pos == pos)

            # Test with different dtypes that must be converted to float32
            for t in [np.int64, np.float64, np.int32]:
                region.set_data(pos=pos.astype(t))
                assert np.all(region._pos == expected_pos)
                assert np.all(region.pos == pos)

            assert_image_approved(c.render(), 'visuals/%s' % reference_image)

            # Check ValueError is raised when pos is not 1D
            assert_raises(ValueError, region.set_data, pos=[[1, 2], [3, 4]])


@requires_application()
def test_linear_region_color():
    """Test the color argument of LinearRegionVisual.set_data() method
    using a single color"""

    # Definition of the region
    pos1 = [5, 42]
    # Definition of the color of the region
    color1 = np.array([0.0, 1.0, 0.0, 0.5], dtype=np.float32)
    # Expected internal color buffer
    color1_expected = np.array([color1, color1, color1, color1],
                               dtype=np.float32)

    with TestingCanvas() as c:
        # Check set_data is working correctly within visual constructor
        region = visuals.LinearRegion(pos=pos1, color=color1, parent=c.scene)
        assert np.all(region._color == color1_expected)
        assert np.all(region.color == color1)

        # Check set_data is working as expected when passing a list as
        # color argument
        region.set_data(color=list(color1))
        assert np.all(region._color == color1_expected)
        assert np.all(region.color == color1)

        # Check set_data is working as expected when passing a tuple as
        # color argument
        region.set_data(color=tuple(color1))
        assert np.all(region._color == color1_expected)
        assert np.all(region.color == color1)

        # Test with different dtypes that must be converted to float32
        region.set_data(color=color1.astype(np.float64))
        assert np.all(region._color == color1_expected)
        assert np.all(region.color == color1)

        assert_image_approved(c.render(), 'visuals/linear_region1.png')

        # Check a ValueError is raised when the length of color argument
        # is not 4.
        assert_raises(ValueError, region.set_data, color=[1.0, 0.5, 0.5])

        # Check a ValueError is raised when too many colors are provided
        assert_raises(ValueError, region.set_data,
                      color=[color1, color1, color1])


@requires_application()
def test_linear_region_gradient():
    """Test LinearRegionVisual with a gradient as color"""

    # Definition of the region
    pos2 = [5, 42, 80]
    # Definition of the color of the region
    color2 = np.array([[0.0, 1.0, 0.0, 0.5],
                       [1.0, 0.0, 0.0, 0.75],
                       [0.0, 0.0, 1.0, 1.0]], dtype=np.float32)
    # Expected internal color buffer
    color2_expected = np.array([color2[0], color2[0],
                                color2[1], color2[1],
                                color2[2], color2[2]],
                               dtype=np.float32)

    with TestingCanvas() as c:
        # Check set_data is working correctly within visual constructor
        region = visuals.LinearRegion(pos=pos2, color=color2, parent=c.scene)
        assert np.all(region._color == color2_expected)
        assert np.all(region.color == color2)

        assert_image_approved(c.render(), 'visuals/linear_region2.png')


run_tests_if_main()
