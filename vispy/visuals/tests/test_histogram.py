# -*- coding: utf-8 -*-
import numpy as np

from vispy.visuals.transforms import STTransform
from vispy.scene.visuals import Histogram
from vispy.testing import (requires_application, TestingCanvas,
                           assert_image_equal, run_tests_if_main)


@requires_application()
def test_histogram():
    """Test histogram visual"""
    size = (200, 100)
    with TestingCanvas(size=size, bgcolor='w') as c:
        data = np.array([0., 0., 1.])
        hist = Histogram(data, bins=2, color='k')
        # the result should be 2 high by 1 wide, so we scale it up
        hist.transform = STTransform((size[0], -size[1] // 2, 1),
                                     (0, size[1]))
        c.draw_visual(hist)
        expected = np.zeros(size[::-1] + (3,))
        expected[:size[1]//2, -size[0]//2:] = 1.
        assert_image_equal("screenshot", expected)


run_tests_if_main()
