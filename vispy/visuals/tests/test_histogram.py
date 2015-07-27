# -*- coding: utf-8 -*-
import numpy as np

from vispy.visuals.transforms import STTransform
from vispy.scene.visuals import Histogram
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@requires_application()
def test_histogram():
    """Test histogram visual"""
    size = (200, 100)
    with TestingCanvas(size=size, bgcolor='w') as c:
        np.random.seed(2397)
        data = np.random.normal(size=100)
        hist = Histogram(data, bins=20, color='k', parent=c.scene)
        hist.transform = STTransform((size[0] // 10, -size[1] // 20, 1),
                                     (100, size[1]))
        assert_image_approved(c.render(), "visuals/histogram.png")


run_tests_if_main()
