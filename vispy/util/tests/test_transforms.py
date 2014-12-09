# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np
from numpy.testing import assert_allclose

from vispy.util.transforms import (translate, scale, xrotate, yrotate,
                                   zrotate, rotate, ortho, frustum,
                                   perspective)
from vispy.testing import run_tests_if_main, assert_equal


def test_transforms():
    """Test basic transforms"""
    xfm = np.random.randn(4, 4).astype(np.float32)

    for rot in [xrotate, yrotate, zrotate]:
        new_xfm = rot(rot(xfm, 90), -90)
        assert_allclose(xfm, new_xfm)

    new_xfm = rotate(rotate(xfm, 90, 1, 0, 0), 90, -1, 0, 0)
    assert_allclose(xfm, new_xfm)

    new_xfm = translate(translate(xfm, 1, -1), 1, -1, 1)
    assert_allclose(xfm, new_xfm)

    new_xfm = scale(scale(xfm, 1, 2, 3), 1, 1. / 2., 1. / 3.)
    assert_allclose(xfm, new_xfm)

    # These could be more complex...
    xfm = ortho(-1, 1, -1, 1, -1, 1)
    assert_equal(xfm.shape, (4, 4))

    xfm = frustum(-1, 1, -1, 1, -1, 1)
    assert_equal(xfm.shape, (4, 4))

    xfm = perspective(1, 1, -1, 1)
    assert_equal(xfm.shape, (4, 4))


run_tests_if_main()
