# -*- coding: utf-8 -*-
import numpy as np
from vispy.scene.visuals import Markers
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.testing.image_tester import assert_image_approved


@requires_application()
def test_markers():
    """Test basic marker / point-sprite support"""
    # this is probably too basic, but it at least ensures that point sprites
    # work for people
    with TestingCanvas() as c:
        marker = Markers()
        np.random.seed(57983)
        marker.set_data(np.random.normal(size=(30, 2), loc=50, scale=10))
        c.draw_visual(marker)
        assert_image_approved("screenshot", "visuals/markers.png")


run_tests_if_main()
