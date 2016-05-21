# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Tests for InfiniteLineVisual
All images are of size (100,100) to keep a small file size
"""

import numpy as np
from vispy import app
from vispy.scene import visuals
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved
from vispy.testing import raises


@requires_application()
def test_set_data():
    """Test InfiniteLineVisual"""

    pos = 5.
    color = [1, 1, 0.5, 0.5]

    for is_vertical in [True, False]:

        with TestingCanvas() as c:
            # Check set_data is working correctly within visual constructor
            region = visuals.InfiniteLine(pos=pos,
                                          color=color,
                                          vertical=is_vertical,
                                          parent=c.scene)
            assert region.pos == pos
            assert np.all(region.color == np.array(color, dtype=np.float32))
            assert region.is_vertical == is_vertical

            if is_vertical:
                assert_image_approved(c.render(), 'visuals/infinite_line.png')
            else:
                assert_image_approved(c.render(),
                                      'visuals/infinite_line_h.png')

            # Only number are accepted
            with raises(TypeError):
                region.set_data(pos=[[1, 2], [3, 4]])

            with raises(ValueError):
                region.set_data(color=[[1, 2], [3, 4]])


run_tests_if_main()
