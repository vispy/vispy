# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Tests for InfiniteLineVisual
All images are of size (100,100) to keep a small file size
"""

import numpy as np

from vispy.scene import visuals
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved
from vispy.testing import assert_raises


@requires_application()
def test_set_data():
    """Test InfiniteLineVisual"""

    pos = 5.0
    color = [1.0, 1.0, 0.5, 0.5]
    expected_color = np.array(color, dtype=np.float32)

    for is_vertical, reference_image in [(True, 'infinite_line.png'),
                                         (False, 'infinite_line_h.png')]:

        with TestingCanvas() as c:
            # Check set_data is working correctly within visual constructor
            region = visuals.InfiniteLine(pos=pos,
                                          color=color,
                                          vertical=is_vertical,
                                          parent=c.scene)
            assert region.pos == pos
            assert np.all(region.color == expected_color)
            assert region.is_vertical == is_vertical

            # Check tuple color argument is accepted
            region.set_data(color=tuple(color))
            assert np.all(region.color == expected_color)

            assert_image_approved(c.render(), 'visuals/%s' % reference_image)

            # Check only numbers are accepted
            assert_raises(TypeError, region.set_data, pos=[[1, 2], [3, 4]])

            # Check color argument can be only a 4 length 1D array
            assert_raises(ValueError, region.set_data, color=[[1, 2], [3, 4]])
            assert_raises(ValueError, region.set_data, color=[1, 2])


run_tests_if_main()
