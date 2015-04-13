# -*- coding: utf-8 -*-
import numpy as np

from vispy.scene.visuals import Image
from vispy.testing import (requires_application, TestingCanvas,
                           assert_image_equal, run_tests_if_main)


@requires_application()
def test_image():
    """Test image visual"""
    size = (100, 50)
    with TestingCanvas(size=size, bgcolor='w') as c:
        for three_d in (True, False):
            shape = size[::-1] + ((3,) if three_d else ())
            data = np.random.rand(*shape)
            image = Image(data, cmap='grays', clim=[0, 1])
            c.draw_visual(image)
            if three_d:
                expected = data
            else:
                expected = np.tile(data[:, :, np.newaxis], (1, 1, 3))
            assert_image_equal("screenshot", expected)


run_tests_if_main()
