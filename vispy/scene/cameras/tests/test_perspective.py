# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import sys

import numpy as np
import pytest

from vispy import scene, io
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@pytest.mark.xfail('darwin' in sys.platform, reason="Differences in OSX rendering")
@requires_application()
def test_perspective_render():
    with TestingCanvas(size=(120, 200)) as canvas:

        grid = canvas.central_widget.add_grid()
        imdata = io.load_crate().astype('float32') / 255

        views = []
        images = []
        for i, imethod in enumerate(['impostor', 'subdivide']):
            v = grid.add_view(row=i, col=0, border_color='white')
            v.camera = 'turntable'
            v.camera.fov = 50
            v.camera.distance = 30

            views.append(v)
            image = scene.visuals.Image(imdata, method=imethod,
                                        grid=(4, 4))
            image.transform = scene.STTransform(translate=(-12.8, -12.8),
                                                scale=(0.1, 0.1))
            v.add(image)
            images.append(image)

        image = canvas.render()
        canvas.close()

        # Allow many pixels to differ by a small amount--texture sampling and
        # exact triangle position will differ across platforms. However a
        # change in perspective or in the widget borders should trigger a
        # failure.
        assert_image_approved(image, 'scene/cameras/perspective_test.png',
                              'perspective test 1: 2 identical views with '
                              'correct perspective',
                              px_threshold=20,
                              px_count=60,
                              max_px_diff=200)


@requires_application()
def test_panzoom_center():
    with TestingCanvas(size=(120, 200)) as canvas:
        grid = canvas.central_widget.add_grid()
        imdata = io.load_crate().astype('float32') / 255

        v = grid.add_view(row=0, col=0)
        v.camera = 'panzoom'

        image = scene.visuals.Image(imdata)
        image.transform = scene.STTransform(translate=(-12.8, -12.8),
                                            scale=(0.1, 0.1))
        v.add(image)

        result1 = canvas.render()[..., :3]
        assert v.camera.center == (0.5, 0.5, 0)

        v.camera.center = (-12.8, -12.8, 0)
        result2 = canvas.render()[..., :3]

        assert not np.allclose(result1, result2)
        # we moved to the lower-left corner of the image that means only the
        # upper-right quadrant should have data, the rest is black background
        np.testing.assert_allclose(result2[100:, :], 0)
        np.testing.assert_allclose(result2[:, :60], 0)
        assert not np.allclose(result2[:100, 60:], 0)
        assert v.camera.center == (-12.8, -12.8, 0)


run_tests_if_main()
