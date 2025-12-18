# -*- coding: utf-8 -*-
import numpy as np
import pytest

from vispy.visuals.transforms import STTransform
from vispy.scene.visuals import Histogram
from vispy.testing import requires_application, TestingCanvas, run_tests_if_main
from vispy.testing.image_tester import assert_image_approved


# mode determines whether we set data during init, after init, or both
@pytest.mark.parametrize("mode", ["init", "post-init", "both"])
@requires_application()
def test_histogram(mode: str):
    """Test histogram visual"""
    size = (200, 100)
    with TestingCanvas(size=size, bgcolor="w") as c:
        np.random.seed(2397)
        data = np.random.normal(size=100)
        init_data = None if mode == "post-init" else data
        hist = Histogram(init_data, bins=20, color="k", parent=c.scene)
        hist.transform = STTransform((size[0] // 10, -size[1] // 20, 1), (100, size[1]))
        if mode != "init":
            hist.set_raw_data(data)
        assert_image_approved(c.render(), "visuals/histogram.png")


run_tests_if_main()
