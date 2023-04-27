# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np
import pytest

from vispy import io
from vispy import scene
from vispy.scene import TurntableCamera
from vispy.testing import (
    requires_application,
    TestingCanvas,
    run_tests_if_main,
)


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


@requires_application()
@pytest.mark.parametrize("camera_type", ("panzoom", "perspective"))
def test_touch_gesture_zoom(camera_type):
    with TestingCanvas(size=(120, 200)) as canvas:
        grid = canvas.central_widget.add_grid()
        imdata = io.load_crate().astype('float32') / 255
        v = grid.add_view(row=0, col=0)
        v.camera = 'panzoom'
        image = scene.visuals.Image(imdata)
        image.transform = scene.STTransform(
            translate=(0, 0),
            scale=(1.0, 1.0),
        )
        v.add(image)

        assert v.camera.rect.pos == (0, 0)
        assert v.camera.rect.size == (1, 1)

        center = v.camera._scene_transform.map((0, 0))[:2]
        canvas.events.touch(
            type="gesture_zoom",
            scale=-1.0,
            pos=center,
        )

        assert v.camera.rect.pos == (0, 0)
        assert v.camera.rect.size == (2, 2)


run_tests_if_main()
