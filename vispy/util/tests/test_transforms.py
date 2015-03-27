# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np
from numpy.testing import assert_allclose

from vispy.util.transforms import (translate, scale, rotate, ortho, frustum,
                                   perspective)
from vispy.testing import run_tests_if_main, assert_equal


def test_transforms():
    """Test basic transforms"""
    xfm = np.random.randn(4, 4).astype(np.float32)

    # Do a series of rotations that should end up into the same orientation
    # again, to ensure the order of computation is all correct
    # i.e. if rotated would return the transposed matrix this would not work
    # out (the translation part would be incorrect)
    new_xfm = (rotate(90, (1, 0, 0)) * rotate(90, (0, 1, 0)) *
               rotate(90, (0, 0, 1)) * rotate(-90, (0, 1, 0)) *
               rotate(180, (1, 0, 0))) * xfm
    assert_allclose(xfm, new_xfm)

    new_xfm = translate((1, -1, 1)) * translate((-1, 1, -1)) * xfm
    assert_allclose(xfm, new_xfm)

    new_xfm = scale((1, 2, 3)) * scale((1, 1. / 2., 1. / 3.)) * xfm
    assert_allclose(xfm, new_xfm)

    # These could be more complex...
    xfm = ortho(-1, 1, -1, 1, -1, 1)
    assert_equal(xfm.shape, (4, 4))

    xfm = frustum(-1, 1, -1, 1, -1, 1)
    assert_equal(xfm.shape, (4, 4))

    xfm = perspective(1, 1, -1, 1)
    assert_equal(xfm.shape, (4, 4))


run_tests_if_main()
