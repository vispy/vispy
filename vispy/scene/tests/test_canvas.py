# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from vispy import scene
from vispy.testing import requires_application, TestingCanvas
from vispy.visuals.transforms import STTransform

import numpy as np


@requires_application()
def test_canvas_render():
    """Test rendering a canvas to an array."""
    with TestingCanvas(size=(800, 600), show=True, title='run') as c:
        view = c.central_widget.add_view()

        im1 = np.zeros((100, 100, 4)).astype(np.float32)
        im1[:, :, 0] = 1
        im1[:, :, 3] = 1

        im2 = np.zeros((50, 50, 4)).astype(np.float32)
        im2[:, :, 1] = 1
        im2[:, :, 3] = 0.4

        # Create the image
        image1 = scene.visuals.Image(im1, parent=view.scene)
        image2 = scene.visuals.Image(im2, parent=view.scene)
        image2.transform = STTransform(translate=(-20, -20, -1))

        rgba_result = c.render()
        rgb_result = c.render(alpha=False)

        # the results should be the same except for alpha
        np.testing.assert_allclose(rgba_result[..., :3], rgb_result)
        # the alpha should have some transparency
        assert (rgba_result[..., 3] != 1).any()
