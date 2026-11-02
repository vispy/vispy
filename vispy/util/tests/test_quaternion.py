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


def test_quaternion_exp_overflow():
    """Preserve NumPy's configurable overflow behavior for real inputs."""
    q = Quaternion(1000, 0, 0, 0, normalize=False)
    with np.errstate(over='raise'):
        assert_raises(FloatingPointError, q.exp)
    with np.errstate(over='ignore'):
        result = q.exp()
    assert np.isinf(result.w)
    assert_allclose((result.x, result.y, result.z), (0, 0, 0))


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


def test_quaternion_log_negative_scalar():
    """Test the logarithm quadrant for a negative scalar and nonzero vector."""
    q = Quaternion(-2, 1, -2, 2, normalize=False)
    angle = np.arccos(-2 / np.sqrt(13))
    assert_allclose(_components(q.log()),
                    (np.log(np.sqrt(13)), angle / 3,
                     -2 * angle / 3, 2 * angle / 3))
    assert_allclose(_components(q.log().exp()), _components(q))


def test_quaternion_norm_extreme_magnitudes():
    """Test norm without squaring overflow or underflow."""
    for value in (1e-200, 1e200):
        q = Quaternion(value, value, value, value, normalize=False)
        assert_allclose(q.norm(), 2 * value, atol=0)


def test_quaternion_log_extreme_vector_magnitudes():
    """Test tiny and large vectors without intermediate scale overflow."""
    for value in (1e-320, 1e-200, 1e200):
        q = Quaternion(0, value, 0, 0, normalize=False)
        assert_allclose(_components(q.log()),
                        (np.log(value), np.pi / 2, 0, 0))


def test_quaternion_log_domain():
    """Test the real-axis branch convention and the undefined zero input."""
    q = Quaternion(-2, 0, 0, 0, normalize=False)
    assert_allclose(_components(q.log()), (np.log(2), np.pi, 0, 0))
    assert_allclose(_components(q.log().exp()), _components(q), atol=1e-15)
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
