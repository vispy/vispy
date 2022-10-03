# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np
import pytest
from vispy.scene.cameras import TurntableCamera
from vispy.testing import run_tests_if_main


@pytest.mark.parametrize(
    "elevation, azimuth, roll, expected",
    [
        [0, 0, 0, np.eye(4)],
        [90, 0, 0, [[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]],
        [0, 90, 0, [[0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]],
        [0, 0, 90, [[0, 0, -1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]]],
    ],
)
def test_turntable_camera_transform(elevation, azimuth, roll, expected):
    camera = TurntableCamera(elevation=elevation, azimuth=azimuth, roll=roll)
    matrix = camera._get_rotation_tr()
    np.testing.assert_allclose(matrix, expected, atol=1e-5)


run_tests_if_main()
