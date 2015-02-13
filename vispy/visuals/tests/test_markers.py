# -*- coding: utf-8 -*-
import numpy as np
from vispy.scene.visuals import Markers
from vispy.testing import (requires_application, TestingCanvas,
                           run_tests_if_main)
from vispy.gloo.util import _screenshot


@requires_application()
def test_markers():
    """Test basic marker / point-sprite support"""
    # this is probably too basic, but it at least ensures that point sprites
    # work for people
    with TestingCanvas() as c:
        marker = Markers()
        marker.set_data(np.array([[50, 50]], np.float32))
        c.draw_visual(marker)
        marker = _screenshot(alpha=False)
        assert marker.any()


run_tests_if_main()
