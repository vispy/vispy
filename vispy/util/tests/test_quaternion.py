# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from numpy.testing import assert_allclose

from vispy.testing import assert_raises, run_tests_if_main
from vispy.util.quaternion import Quaternion


def _components(q):
    return q.w, q.x, q.y, q.z


def test_quaternion_exp():
    """Test quaternion exponential for real and imaginary inputs."""
    q = Quaternion(0, 0, 0, np.pi / 4, normalize=False)
    assert_allclose(_components(q.exp()),
                    (np.sqrt(0.5), 0, 0, np.sqrt(0.5)))

    q = Quaternion(np.log(2), 0, 0, 0, normalize=False)
    assert_allclose(_components(q.exp()), (2, 0, 0, 0))


def test_quaternion_log():
    """Test quaternion logarithm for unit and non-unit inputs."""
    assert_allclose(_components(Quaternion().log()), (0, 0, 0, 0))

    q = Quaternion(0, 2, 0, 0, normalize=False)
    assert_allclose(_components(q.log()), (np.log(2), np.pi / 2, 0, 0))

    q = Quaternion(2, 1, -2, 2, normalize=False)
    angle = np.arccos(2 / np.sqrt(13))
    assert_allclose(_components(q.log()),
                    (np.log(np.sqrt(13)), angle / 3,
                     -2 * angle / 3, 2 * angle / 3))


def test_quaternion_log_domain():
    """Test inputs without a unique finite quaternion logarithm."""
    assert_raises(ValueError, Quaternion(-2, 0, 0, 0,
                                         normalize=False).log)
    assert_raises(ValueError, Quaternion(0, 0, 0, 0,
                                         normalize=False).log)


def test_quaternion_exp_log_round_trip():
    """Test that exp(log(q)) recovers a non-real quaternion."""
    q = Quaternion(2, 1, -2, 2, normalize=False)
    assert_allclose(_components(q.log().exp()), _components(q))

    for x in (1e-8, 1e-12, 1e-16):
        q = Quaternion(1, x, 0, 0, normalize=False)
        assert_allclose(_components(q.log().exp()), _components(q))


run_tests_if_main()
